from unittest.mock import MagicMock, call

import pkg_resources
import pytest
from google.cloud import exceptions

from prowjobsscraper.equinix import EquinixExtractor
from prowjobsscraper.prowjob import (
    EquinixMetadata,
    EquinixMetadataOperationSystem,
    ProwJobs,
)


@pytest.mark.parametrize(
    "cloud_cluster_profile, side_effect, expected_metadata_path",
    [
        (  # try to download from baremetalds-packet-gather-metadata directory...
            "packet-assisted",
            [],
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/baremetalds-packet-gather-metadata/artifacts/equinix-metadata.json",
        ),
        (  # else try to download from assisted-baremetal-gather directory...
            "packet-assisted",
            [exceptions.ClientError("not baremetalds-packet-gather-metadata")],
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/assisted-baremetal-gather/artifacts/equinix-metadata.json",
        ),
        (  # else try to download from assisted-baremetal-operator-gather
            "packet-assisted",
            [
                exceptions.ClientError("not baremetalds-packet-gather-metadata"),
                exceptions.ClientError("not assisted-baremetal-gather"),
            ],
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/assisted-baremetal-operator-gather/artifacts/equinix-metadata.json",
        ),
        (  # else try to download from assisted-common-gather
            "packet-assisted",
            [
                exceptions.ClientError("not baremetalds-packet-gather-metadata"),
                exceptions.ClientError("not assisted-baremetal-gather"),
                exceptions.ClientError("not assisted-baremetal-operator-gather"),
            ],
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/assisted-common-gather/artifacts/equinix-metadata.json",
        ),
        (  # try to download from baremetalds-packet-gather-metadata
            "packet-sno",
            [],
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/baremetalds-packet-gather-metadata/artifacts/equinix-metadata.json",
        ),
        (  # else try to download from baremetalds-sno-gather
            "packet-sno",
            [exceptions.ClientError("not baremetalds-packet-gather-metadata")],
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/baremetalds-sno-gather/artifacts/equinix-metadata.json",
        ),
    ],
)
def test_hydrate_equinix_should_succeed_when_metadata_are_available(
    cloud_cluster_profile, side_effect, expected_metadata_path
):
    jobs = ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, "equinix_assets/prowjobs.json")
    )
    jobs.items[0].metadata.labels.cloudClusterProfile = cloud_cluster_profile

    equinix_metadata = pkg_resources.resource_string(
        __name__, "equinix_assets/equinix-metadata.json"
    )
    side_effect.append(equinix_metadata)

    expected_metadata = EquinixMetadata(
        facility="dc13",
        hostname="ipi-ci-op-yvdlzmdn-98f49-1551908182547238912",
        id="47bd6216-1345-4813-aa19-c0b5648b744a",
        metro="dc",
        operating_system=EquinixMetadataOperationSystem(
            slug="rocky_8", image_tag="1864658f8cc7117649908fe0acafa264f13d5b1b"
        ),
        plan="c3.medium.x86",
    )

    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.download_as_string.side_effect = side_effect

    equinix = EquinixExtractor(storage_client)
    equinix.hydrate(jobs)

    storage_client.bucket.assert_called_with("origin-ci-test")
    bucket.blob.assert_called_with(expected_metadata_path)

    assert jobs.items[0].equinixMetadata == expected_metadata


def test_hydrate_equinix_should_not_fail_when_metadata_are_missing():
    jobs = ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"equinix_assets/prowjobs.json")
    )

    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.download_as_string.side_effect = exceptions.ClientError("test")

    equinix = EquinixExtractor(storage_client)
    equinix.hydrate(jobs)

    storage_client.bucket.assert_called_with("origin-ci-test")
    assert bucket.blob.call_args_list == [
        call(
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/baremetalds-packet-gather-metadata/artifacts/equinix-metadata.json"
        ),
        call(
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/assisted-baremetal-gather/artifacts/equinix-metadata.json"
        ),
        call(
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/assisted-baremetal-operator-gather/artifacts/equinix-metadata.json"
        ),
        call(
            "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/e2e-metal-assisted/assisted-common-gather/artifacts/equinix-metadata.json"
        ),
    ]

    assert jobs.items[0].equinixMetadata == None


def test_hydrate_equinix_should_skip_when_non_equinix_job():
    jobs = ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"equinix_assets/prowjobs.json")
    )

    jobs.items[
        0
    ].metadata.labels.cloudClusterProfile = "not-equinix-cloud-cluster-profile"

    storage_client = MagicMock()
    equinix = EquinixExtractor(storage_client)
    equinix.hydrate(jobs)

    storage_client.bucket.assert_not_called()
    assert jobs.items[0].equinixMetadata is None
