import json
from pathlib import Path
from typing import Final

import pytest
from pydantic import ValidationError
from pytest_httpserver import HTTPServer

from prowjobsscraper import prowjob

INVALID_RESPONSE_FROM_PROW: Final[
    str
] = """
{"invalid": "value"}
"""


def test_invalid_json_from_prow_should_throw_an_exception(httpserver: HTTPServer):
    httpserver.expect_request("/jobs").respond_with_json(INVALID_RESPONSE_FROM_PROW)
    with pytest.raises(ValidationError):
        prowjob.ProwJobs.create_from_url(httpserver.url_for("/jobs"))


def test_valid_json_from_prow_should_be_successfully_parsed(httpserver: HTTPServer):
    response = (
        Path(__file__).parent / f"prowjob_assets/valid_prow_response.json"
    ).read_bytes()
    expected = json.loads(
        (Path(__file__).parent / f"prowjob_assets/expected_prowjobs.json").read_bytes()
    )
    httpserver.expect_request("/jobs").respond_with_data(response)
    jobs = prowjob.ProwJobs.create_from_url(httpserver.url_for("/jobs"))

    assert jobs.json() == json.dumps(expected)


@pytest.mark.parametrize(
    "job_name, job_type, job_variant",
    [
        (
            "periodic-ci-openshift-assisted-service-master-edge-e2e-metal-assisted",
            "periodic",
            "edge",
        ),
        (
            "pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted",
            "presubmit",
            "edge",
        ),
        (
            "pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted",
            "batch",
            "edge",
        ),
        (
            "branch-ci-openshift-assisted-service-master-edge-e2e-metal-assisted",
            "postsubmit",
            "edge",
        ),
        (
            "periodic-ci-openshift-assisted-service-master-e2e-metal-assisted",
            "periodic",
            None,
        ),
        (
            "rehearse-4121-pull-ci-openshift-cluster-baremetal-operator-release-ocm-2.5-e2e-metal-assisted",
            "presubmit",
            None,
        ),
    ],
)
def test_context_should_be_successfully_parsed(job_name, job_type, job_variant):
    jobs = prowjob.ProwJobs.create_from_string(
        (Path(__file__).parent / "prowjob_assets/valid_prow_response.json").read_bytes()
    )
    jobs.items[0].spec.type = job_type
    jobs.items[0].spec.job = job_name
    jobs.items[0].metadata.labels.variant = job_variant

    assert jobs.items[0].context == "e2e-metal-assisted"
