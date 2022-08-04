import json
from datetime import timedelta
from unittest.mock import MagicMock

import pkg_resources
from google.cloud import exceptions

from prowjobsscraper import step
from prowjobsscraper.prowjob import ProwJobs


def test_step_extractor_when_junit_is_not_available_should_return_no_steps():
    jobs = ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"step_assets/prowjobs.json")
    )
    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.download_as_string.side_effect = exceptions.ClientError("test")

    step_extractor = step.StepExtractor(storage_client)
    steps = step_extractor.parse_prow_jobs(jobs)

    storage_client.bucket.assert_called_once_with("origin-ci-test")
    bucket.blob.assert_called_once_with(
        "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/junit_operator.xml"
    )
    assert len(steps) == 0


def test_step_extractor_with_valid_junit_should_return_steps():
    jobs = ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"step_assets/prowjobs.json")
    )
    junit = pkg_resources.resource_string(__name__, f"step_assets/junit_operator.xml")

    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.download_as_string.return_value = junit

    step_extractor = step.StepExtractor(storage_client)
    steps = step_extractor.parse_prow_jobs(jobs)

    storage_client.bucket.assert_called_once_with("origin-ci-test")
    bucket.blob.assert_called_once_with(
        "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/junit_operator.xml"
    )

    assert {s.name for s in steps} == {"step1", "step2", "step3"}
    for s in steps:
        expected = json.loads(
            pkg_resources.resource_string(
                __name__, f"step_assets/expected_{s.name}.json"
            )
        )
        assert s.json(exclude_unset=True) == json.dumps(expected)


def test_step_extractor_with_malformed_junit_should_return_steps():
    jobs = ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"step_assets/prowjobs.json")
    )
    junit = pkg_resources.resource_string(
        __name__, f"step_assets/malformed_time_junit_operator.xml"
    )

    storage_client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    storage_client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.download_as_string.return_value = junit

    step_extractor = step.StepExtractor(storage_client)
    steps = step_extractor.parse_prow_jobs(jobs)

    storage_client.bucket.assert_called_once_with("origin-ci-test")
    bucket.blob.assert_called_once_with(
        "pr-logs/pull/openshift_assisted-service/4121/pull-ci-openshift-assisted-service-master-edge-e2e-metal-assisted/1549300279667593216/artifacts/junit_operator.xml"
    )
    assert len(steps) == 1
    assert steps[0].duration == timedelta(0)
    assert steps[0].name == "step1"
