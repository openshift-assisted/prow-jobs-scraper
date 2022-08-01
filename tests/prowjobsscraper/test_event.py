from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch

import pkg_resources

from prowjobsscraper import event, step


def test_indices_should_be_created_when_required():
    def exists_side_effect(index: str, **kwargs):
        """
        Side effect to simulate that jobs index already exists while steps index need to be created.
        """
        return index.startswith("jobs")

    es_client = MagicMock()
    es_client.indices.exists.side_effect = exists_side_effect

    event.EventStoreElastic(
        client=es_client, job_index_basename="jobs", step_index_basename="steps"
    )

    expected_index_suffix = datetime.now().strftime("%Y.%W")
    expected_calls_exists = [
        call(index=f"jobs-{expected_index_suffix}"),
        call(index=f"steps-{expected_index_suffix}"),
    ]
    assert es_client.indices.exists.call_count == 2
    es_client.indices.exists.assert_has_calls(expected_calls_exists, any_order=True)

    es_client.indices.create.assert_called_once()
    assert "body" in es_client.indices.create.call_args.kwargs
    assert (
        es_client.indices.create.call_args.kwargs["index"]
        == f"steps-{expected_index_suffix}"
    )


@patch("opensearchpy.helpers.scan")
def test_scan_build_id_when_results_are_expected(scan):
    es_client = MagicMock()
    scan.return_value = [
        {"_source": {"job": {"build_id": 1}}},
        {"_source": {"job": {"build_id": 2}}},
        {"_source": {"job": {"build_id": 3}}},
    ]
    event_store = event.EventStoreElastic(
        client=es_client, job_index_basename="jobs", step_index_basename="steps"
    )
    build_ids = event_store.scan_build_ids()

    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)
    expected_index_suffix = now.strftime("%Y.%W")
    expected_index_previous_suffix = a_week_ago.strftime("%Y.%W")
    expected_search_indices = (
        f"jobs-{expected_index_suffix},jobs-{expected_index_previous_suffix}"
    )

    scan.assert_called_once()
    assert scan.call_args.kwargs["index"] == expected_search_indices
    assert build_ids == {1, 2, 3}


@patch("opensearchpy.helpers.scan", return_value=[])
def test_scan_build_id_when_no_results(scan):
    es_client = MagicMock()

    event_store = event.EventStoreElastic(
        client=es_client, job_index_basename="jobs", step_index_basename="steps"
    )
    build_ids = event_store.scan_build_ids()

    scan.assert_called_once()
    assert len(build_ids) == 0


@patch("opensearchpy.helpers.bulk", return_value=[])
def test_index_job_step_when_successful(bulk):
    expected_step_index = datetime.now().strftime("steps-%Y.%W")

    job_step = step.JobStep.parse_raw(
        pkg_resources.resource_string(__name__, f"event_assets/jobstep.json")
    )

    es_client = MagicMock()
    event_store = event.EventStoreElastic(
        client=es_client, job_index_basename="jobs", step_index_basename="steps"
    )

    event_store.index_job_steps(steps=[job_step])
    bulk.assert_called_once()
    assert bulk.call_args.args[0] == es_client

    expected_job_step = event.StepEvent.create_from_job_step(job_step).dict()
    expected_job_step["_index"] = expected_step_index
    indexed_job_step = list(bulk.call_args.args[1])
    assert indexed_job_step[0] == expected_job_step

    es_client.indices.refresh.assert_called_once_with(index=expected_step_index)


@patch("opensearchpy.helpers.bulk")
def test_index_prow_job_when_successful(bulk):
    expected_job_index = datetime.now().strftime("jobs-%Y.%W")

    job_step = step.JobStep.parse_raw(
        pkg_resources.resource_string(__name__, f"event_assets/jobstep.json")
    )
    prow_job = job_step.job

    es_client = MagicMock()
    event_store = event.EventStoreElastic(
        client=es_client, job_index_basename="jobs", step_index_basename="steps"
    )

    event_store.index_prow_jobs(jobs=[prow_job])

    # check that bulk was called with the client and that "_index" key was appended to the document
    bulk.assert_called_once()
    assert bulk.call_args.args[0] == es_client

    expected_prow_job = event.JobEvent.create_from_prow_job(prow_job).dict()
    expected_prow_job["_index"] = expected_job_index
    indexed_prow_job = list(bulk.call_args.args[1])
    assert indexed_prow_job[0] == expected_prow_job

    es_client.indices.refresh.assert_called_once_with(index=expected_job_index)


def test_job_step_successfully_parse_into_step_event():
    job_step = step.JobStep.parse_raw(
        pkg_resources.resource_string(__name__, f"event_assets/jobstep.json")
    )
    step_event = event.StepEvent.create_from_job_step(job_step)

    expected_step_event = event.StepEvent.parse_raw(
        pkg_resources.resource_string(
            __name__, f"event_assets/expected_step_event.json"
        )
    )

    assert step_event == expected_step_event
