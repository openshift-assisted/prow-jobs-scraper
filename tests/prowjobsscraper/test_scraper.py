from unittest.mock import MagicMock

import pkg_resources
import pytest
from pytest_httpserver import HTTPServer

from prowjobsscraper import equinix_usages, prowjob, scraper, step


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
def test_job_filtering(job_name, job_state, job_description, is_valid_job):
    jobs = prowjob.ProwJobs.create_from_string(
        pkg_resources.resource_string(__name__, f"scraper_assets/prowjob.json")
    )

    event_store = MagicMock()
    event_store.scan_build_ids_from_index.return_value = []

    step_extractor = MagicMock()
    step_extractor.parse_prow_jobs.return_value = []

    equinix_metadata_extractor = MagicMock()
    equinix_usages_extractor = MagicMock()

    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadata_extractor,
        equinix_usages_extractor,
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
    equinix_usages_extractor = MagicMock()

    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadata_extractor,
        equinix_usages_extractor,
    )
    jobs.items[0].spec.job = "e2e-blala-assisted"
    jobs.items[0].status.state = "success"
    scrape.execute(jobs.copy(deep=True))
    equinix_metadata_extractor.hydrate.assert_called_once()
    event_store.index_prow_jobs.assert_called_once_with([])


def test_existing_usages_in_event_store_are_filtered_out():
    usages = [
        {
            "description": None,
            "end_date": "2023-03-31T23:59:59Z",
            "facility": "dc13",
            "metro": "dc",
            "name": "ipi-ci-op-nnk50j82-5ed26-1634705984507088896",
            "plan": "Outbound Bandwidth",
            "plan_version": "Outbound Bandwidth",
            "price": 0.05,
            "quantity": 2,
            "start_date": "2023-03-01T00:00:00Z",
            "total": 0.1,
            "type": "Instance",
            "unit": "GB",
        },
        {
            "description": None,
            "end_date": "2023-03-31T23:59:59Z",
            "facility": "am6",
            "metro": "am",
            "name": "ipi-ci-op-tb33cyhd-20a45-1638140834400440320",
            "plan": "Outbound Bandwidth",
            "plan_version": "Outbound Bandwidth",
            "price": 0.05,
            "quantity": 4,
            "start_date": "2023-03-01T00:00:00Z",
            "total": 0.2,
            "type": "Instance",
            "unit": "GB",
        },
        {
            "description": None,
            "facility": "dc13",
            "metro": "dc",
            "name": "ipi-ci-op-3i64pdkt-0f69d-1633695483341836288",
            "plan": "Outbound Bandwidth",
            "plan_version": "Outbound Bandwidth",
            "price": 0.05,
            "quantity": 3,
            "start_date": "2023-03-01T00:00:00Z",
            "total": 0.15,
            "type": "Instance",
            "unit": "GB",
        },
    ]

    event_store = MagicMock()
    event_store.scan_build_ids_from_index.return_value = {"1633695483341836288"}

    step_extractor = MagicMock()
    step_extractor.parse_prow_jobs.return_value = []

    equinix_metadata_extractor = MagicMock()
    equinix_usages_extractor = MagicMock()
    equinix_usages_extractor.get_project_usages.return_value = [
        equinix_usages.EquinixUsage.parse_obj(usage) for usage in usages
    ]

    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadata_extractor,
        equinix_usages_extractor,
    )

    prow_jobs = MagicMock()
    prow_jobs.items = []

    scrape.execute(prow_jobs)
    assert len(event_store.index_equinix_usages.call_args[0][0]) == 2


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
    equinix_usages_extractor = MagicMock()

    scrape = scraper.Scraper(
        event_store,
        step_extractor,
        equinix_metadata_extractor,
        equinix_usages_extractor,
    )
    scrape.execute(jobs.copy(deep=True))
    equinix_metadata_extractor.hydrate.assert_called_once()
    event_store.index_prow_jobs.assert_called_once_with(jobs.items)
    event_store.index_job_steps.assert_called_once_with([jobstep])
