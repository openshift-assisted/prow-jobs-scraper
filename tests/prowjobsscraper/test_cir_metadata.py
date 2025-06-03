from types import SimpleNamespace
from unittest.mock import MagicMock

import google.cloud.exceptions as gcs_exceptions
import pkg_resources
import pytest

from providers.aws import ProviderAWS
from providers.equinix import ProviderEquinix
from providers.ibm_cloud import ProviderIBMCloud
from prowjobsscraper.cir_metadata import CIResourceMetadataExtractor


def make_prow_job(
    packet_profile=None, url="gs://bucket/path", context="ctx", job_name="job1"
):
    labels = SimpleNamespace(cloudClusterProfile=packet_profile)
    metadata = SimpleNamespace(labels=labels)
    status = SimpleNamespace(url=url)
    spec = SimpleNamespace(job=job_name)
    return SimpleNamespace(metadata=metadata, status=status, context=context, spec=spec)


class DummyProvider:
    def __init__(self, region, hostname, os_):
        self.id = "dummy"
        self._region = region
        self._hostname = hostname
        self._os = os_

    def get_provider_metadata_from_prowjob(self, prowjob, gcs_client, gcs_bucket_name):
        return SimpleNamespace(
            region=self._region, hostname=self._hostname, os=self._os
        )


def test_get_metadata_success(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    monkeypatch.setattr(
        "prowjobsscraper.utils.download_from_gcs_as_string",
        lambda client, bucket, path: "raw-data",
    )
    assert extractor._get_metadata("some/path") == "raw-data"


def test_get_metadata_client_error(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )

    def raise_error(client, bucket, path):
        raise gcs_exceptions.ClientError("not found")

    monkeypatch.setattr(
        "prowjobsscraper.utils.download_from_gcs_as_string", raise_error
    )
    assert extractor._get_metadata("bad/path") is None


def test_get_cir_metadata_success(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile="packet-profile")
    monkeypatch.setattr(extractor, "_get_metadata", lambda path: "raw-json")
    dummy_meta = SimpleNamespace(provider="prov-id")
    monkeypatch.setattr(
        "prowjobsscraper.cir_metadata.CIResourceMetadata.parse_raw",
        lambda raw: dummy_meta,
    )
    result = extractor._get_cir_metadata(base_path="base", job=job)
    assert result is dummy_meta


def test_get_cir_metadata_no_metadata(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile="packet")
    monkeypatch.setattr(extractor, "_get_metadata", lambda path: None)
    assert extractor._get_cir_metadata(base_path="base", job=job) is None


def test_get_cir_metadata_decode_error(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile="packet")
    monkeypatch.setattr(extractor, "_get_metadata", lambda path: "bad-json")

    def parse_fail(raw):
        raise ValueError("fail to parse")

    monkeypatch.setattr(
        "prowjobsscraper.cir_metadata.CIResourceMetadata.parse_raw", parse_fail
    )
    assert extractor._get_cir_metadata(base_path="base", job=job) is None


def test_should_job_have_metadata_true():
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile="my-packet")
    assert extractor._should_job_have_metadata(job)


def test_should_job_have_metadata_false():
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile=None)
    assert not extractor._should_job_have_metadata(job)


def test_set_cir_metadata_assigns(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile="packet-group", url="gs://b/p", context="ctx1")

    monkeypatch.setattr(extractor, "_should_job_have_metadata", lambda job: True)
    monkeypatch.setattr(
        "prowjobsscraper.utils.get_gcs_base_path_from_job_url", lambda url: "base-path"
    )

    dummy_cir = SimpleNamespace(provider="dummy", region=None, hostname=None, os=None)
    monkeypatch.setattr(extractor, "_get_cir_metadata", lambda base, job: dummy_cir)

    provider = DummyProvider(region="r1", hostname="h1", os_="o1")
    monkeypatch.setattr(
        "prowjobsscraper.cir_metadata.get_provider_by_id",
        lambda id: provider if id == "dummy" else None,
        raising=True,
    )

    extractor._set_cir_metadata(job)

    assert hasattr(job, "cirMetadata")
    assert job.cirMetadata is dummy_cir
    assert dummy_cir.region == "r1"
    assert dummy_cir.hostname == "h1"
    assert dummy_cir.os == "o1"


def test_set_cir_metadata_skips_non_packet(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile=None)
    called = False

    def fake_set(job):
        nonlocal called
        called = True

    monkeypatch.setattr(
        extractor, "_get_cir_metadata", lambda base, job: SimpleNamespace()
    )
    extractor._set_cir_metadata(job)
    assert not hasattr(job, "cirMetadata")


def test_set_cir_metadata_skips_unknown_provider(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job = make_prow_job(packet_profile="packet", url="gs://b/p", context="ctx")

    monkeypatch.setattr(extractor, "_should_job_have_metadata", lambda job: True)
    monkeypatch.setattr(
        "prowjobsscraper.utils.get_gcs_base_path_from_job_url",
        lambda url: "base-path",
    )
    dummy_cir = SimpleNamespace(
        provider="no-such-provider", region=None, hostname=None, os=None
    )
    monkeypatch.setattr(extractor, "_get_cir_metadata", lambda base, job: dummy_cir)
    monkeypatch.setattr(
        "prowjobsscraper.cir_metadata.get_provider_by_id",
        lambda id: None,
    )

    extractor._set_cir_metadata(job)

    assert not hasattr(job, "cirMetadata")


def test_hydrate_calls_set_for_each_job(monkeypatch):
    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job1 = make_prow_job(packet_profile="packet", url="gs://b1", context="ctx1")
    job2 = make_prow_job(packet_profile="packet", url="gs://b2", context="ctx2")
    jobs = SimpleNamespace(items=[job1, job2])
    calls = []
    monkeypatch.setattr(extractor, "_set_cir_metadata", lambda job: calls.append(job))

    extractor.hydrate(jobs)

    assert calls == [job1, job2]


def test_hydrate_integration_with_providers(monkeypatch):
    cir_json_ibm = pkg_resources.resource_string(
        __name__, "cir_metadata_assets/cir_ibm_metadata.json"
    ).decode()
    equinix_json = pkg_resources.resource_string(
        __name__, "cir_metadata_assets/equinix_metadata.json"
    ).decode()
    cir_json_equinix = pkg_resources.resource_string(
        __name__, "cir_metadata_assets/cir_equinix_metadata.json"
    ).decode()
    ibm_json = pkg_resources.resource_string(
        __name__, "cir_metadata_assets/ibm_metadata.json"
    ).decode()
    cir_json_aws = pkg_resources.resource_string(
        __name__, "cir_metadata_assets/cir_aws_metadata.json"
    ).decode()
    aws_json = pkg_resources.resource_string(
        __name__, "cir_metadata_assets/aws_metadata.json"
    ).decode()

    extractor = CIResourceMetadataExtractor(
        client=MagicMock(), gcs_bucket_name="bucket"
    )
    job_equinix = make_prow_job(
        packet_profile="packet", url="gs://b/p_e", context="ctx_equinix"
    )
    job_ibm = make_prow_job(
        packet_profile="packet", url="gs://b/p_i", context="ctx_ibm"
    )
    job_aws = make_prow_job(
        packet_profile="packet", url="gs://b/p_a", context="ctx_aws"
    )
    jobs = SimpleNamespace(items=[job_equinix, job_ibm, job_aws])

    monkeypatch.setattr(extractor, "_should_job_have_metadata", lambda job: True)
    monkeypatch.setattr(
        "prowjobsscraper.utils.get_gcs_base_path_from_job_url", lambda url: "base"
    )

    def fake_download(client, bucket, path):
        # cir.json path
        if path.endswith("cir.json"):
            if "ctx_equinix" in path:
                return cir_json_equinix
            if "ctx_ibm" in path:
                return cir_json_ibm
            if "ctx_aws" in path:
                return cir_json_aws
        # metadata files
        if path.endswith("equinix-metadata.json"):
            return equinix_json
        if path.endswith("ibm-classic-metadata.json"):
            return ibm_json
        if path.endswith("aws-metadata.json"):
            return aws_json
        return None

    monkeypatch.setattr(
        "prowjobsscraper.utils.download_from_gcs_as_string", fake_download
    )

    equinix_provider = ProviderEquinix()
    ibm_provider = ProviderIBMCloud()
    aws_provider = ProviderAWS()

    monkeypatch.setattr(
        "providers.provider.get_provider_by_id",
        lambda id: (
            equinix_provider
            if id == "equinix"
            else ibm_provider if id == "ibm-classic" else aws_provider
        ),
    )

    extractor.hydrate(jobs)

    # Equinix assertions
    assert job_equinix.cirMetadata.region == "da"
    assert job_equinix.cirMetadata.hostname == "ofcir-e4b5beed1d5f4e6db551638e01f63a9a"
    assert job_equinix.cirMetadata.os == "rocky_9"

    # IBM assertions
    assert job_ibm.cirMetadata.region == "dal10"
    assert job_ibm.cirMetadata.hostname == "assisted-medium-01.redhat.com"
    assert job_ibm.cirMetadata.os == "Rocky Linux 9.2-64"

    # AWS assertions
    assert job_aws.cirMetadata.region == "us-east-1"
    assert job_aws.cirMetadata.hostname == "i-03c9cfc7f80c31c90"
    assert job_aws.cirMetadata.os == "ami-0a73e96a849c232cc"
