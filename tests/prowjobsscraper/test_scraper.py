from datetime import datetime, timezone
from typing import Literal
from unittest.mock import MagicMock

import pkg_resources
import pytest
from pytest_httpserver import HTTPServer

from prowjobsscraper import prowjob, scraper, step


@pytest.mark.parametrize(
    "job_name, job_state,job_description,is_valid_job",
    [
        (  # <something>-openshift-assisted-<something> must be taken
            "pull-ci-openshift-assisted-service-master-edge-subsystem-kubeapi-aws",
            "success",
            "",
            True,
        ),
        (  # failures must be taken
            "pull-ci-openshift-assisted-service-master-edge-subsystem-kubeapi-aws",
            "failure",
            "",
            True,
        ),
        (  # pending jobs must be skipped
            "pull-ci-openshift-assisted-service-master-edge-subsystem-kubeapi-aws",
            "pending",
            "",
            False,
        ),
        (  # overridden jobs must be skipped
            "pull-ci-openshift-assisted-service-master-edge-subsystem-kubeapi-aws",
            "success",
            "Overridden by Batman",
            False,
        ),
        (  # openshift-<something>-assisted must be taken
            "openshift-origin-27159-nightly-4.11-e2e-metal-assisted",
            "success",
            "",
            True,
        ),
        (  # fast-forward jobs must be skipped
            "periodic-openshift-release-fast-forward-assisted-service",
            "success",
            "",
            False,
        ),
    ],
)
def test_job_filtering(
    job_name: Literal[
        "pull-ci-openshift-assisted-service-master-edge-sub…",
        "openshift-origin-27159-nightly-4.11-e2e-metal-assi…",
        "periodic-openshift-release-fast-forward-assisted-s…",
    ],
    job_state: Literal["success", "failure", "pending"],
    job_description: Literal["", "Overridden by Batman"],
    is_valid_job: bool,
):
    jobs = prowjob.ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"scraper_assets/prowjob.json")
    )

    event_store = MagicMock()
    event_store.scan_build_ids_from_index.return_value = []

    step_extractor = MagicMock()
    step_extractor.parse_prow_jobs.return_value = []

    equinix_metadata_extractor = MagicMock()

    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadata_extractor,
    )

    jobs.items[0].spec.job = job_name
    jobs.items[0].status.state = job_state
    jobs.items[0].status.description = job_description
    scrape.execute(jobs)

    equinix_metadata_extractor.hydrate.assert_called_once()

    if is_valid_job:
        event_store.index_prow_jobs.assert_called_once_with(jobs.items)
    else:
        event_store.index_prow_jobs.assert_called_once_with([])


def test_existing_jobs_in_event_store_are_filtered_out():
    jobs = prowjob.ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"scraper_assets/prowjob.json")
    )

    event_store = MagicMock()
    event_store.scan_build_ids_from_index.return_value = [jobs.items[0].status.build_id]

    step_extractor = MagicMock()
    step_extractor.parse_prow_jobs.return_value = []

    equinix_metadata_extractor = MagicMock()

    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadata_extractor,
    )
    jobs.items[0].spec.job = "e2e-blala-assisted"
    jobs.items[0].status.state = "success"
    scrape.execute(jobs.copy(deep=True))
    equinix_metadata_extractor.hydrate.assert_called_once()
    event_store.index_prow_jobs.assert_called_once_with([])


def test_jobs_and_steps_are_indexed():
    jobstep = step.JobStep.parse_raw(
        pkg_resources.resource_string(__name__, f"scraper_assets/jobstep.json")
    )
    jobs = prowjob.ProwJobs(items=[jobstep.job])

    event_store = MagicMock()
    event_store.scan_build_ids_from_index.return_value = []

    step_extractor = MagicMock()
    step_extractor.parse_prow_jobs.return_value = [jobstep]

    equinix_metadata_extractor = MagicMock()

    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadata_extractor,
    )
    scrape.execute(jobs.copy(deep=True))
    equinix_metadata_extractor.hydrate.assert_called_once()
    event_store.index_prow_jobs.assert_called_once_with(jobs.items)
    event_store.index_job_steps.assert_called_once_with([jobstep])
