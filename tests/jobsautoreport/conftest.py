from datetime import datetime, timedelta

import pytest

from jobsautoreport.models import (
    IdentifiedJobMetrics,
    JobIdentifier,
    JobMetrics,
    JobType,
    PeriodicJobsReport,
    PostSubmitJobsReport,
    PresubmitJobsReport,
    Report,
)


@pytest.fixture
def mock_report_1():
    mock_job_metrics_1 = JobMetrics(
        successes=9,
        failures=1,
        flakiness=0.05,
    )

    mock_job_identifier_1 = JobIdentifier(
        name="test-job-1",
        repository="sample-repo-1",
        base_ref="master",
        context="test-context-1",
    )

    mock_identified_job_metrics_1 = IdentifiedJobMetrics(
        job_identifier=mock_job_identifier_1, metrics=mock_job_metrics_1
    )

    mock_periodics_report = PeriodicJobsReport(
        type=JobType.PERIODIC,
        total=10,
        successes=9,
        failures=1,
        success_rate=90.0,
        top_10_failing=[mock_identified_job_metrics_1],
    )

    mock_presubmits_report = PresubmitJobsReport(
        type=JobType.PRESUBMIT,
        total=11,
        successes=9,
        failures=2,
        success_rate=82.0,
        top_10_failing=[mock_identified_job_metrics_1],
        rehearsals=2,
    )

    mock_postsubmits_report = PostSubmitJobsReport(
        type=JobType.POSTSUBMIT,
        total=7,
        successes=6,
        failures=1,
        success_rate=86.0,
        top_10_failing=[mock_identified_job_metrics_1],
    )

    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    one_week_ago = datetime.now() - timedelta(weeks=1)

    return Report(
        from_date=two_weeks_ago,
        to_date=one_week_ago,
        periodics_report=mock_periodics_report,
        presubmits_report=mock_presubmits_report,
        postsubmits_report=mock_postsubmits_report,
        top_5_most_triggered_e2e_or_subsystem_jobs=[mock_identified_job_metrics_1],
        flaky_jobs=[mock_identified_job_metrics_1],
    )


@pytest.fixture
def mock_report_2():
    mock_job_metrics_2 = JobMetrics(
        successes=7,
        failures=3,
        flakiness=0.15,
    )

    mock_job_identifier_2 = JobIdentifier(
        name="test-job-2",
        repository="sample-repo-2",
        base_ref="dev",
        context="test-context-2",
    )

    mock_identified_job_metrics_2 = IdentifiedJobMetrics(
        job_identifier=mock_job_identifier_2, metrics=mock_job_metrics_2
    )

    mock_periodics_report = PeriodicJobsReport(
        type=JobType.PERIODIC,
        total=10,
        successes=7,
        failures=3,
        success_rate=70.0,
        top_10_failing=[mock_identified_job_metrics_2],
    )

    mock_presubmits_report = PresubmitJobsReport(
        type=JobType.PRESUBMIT,
        total=12,
        successes=8,
        failures=4,
        success_rate=67.0,
        top_10_failing=[mock_identified_job_metrics_2],
        rehearsals=3,
    )

    mock_postsubmits_report = PostSubmitJobsReport(
        type=JobType.POSTSUBMIT,
        total=0,
        successes=0,
        failures=0,
        success_rate=None,
        top_10_failing=[],
    )

    three_weeks_ago = datetime.now() - timedelta(weeks=3)
    two_weeks_ago = datetime.now() - timedelta(weeks=2)

    return Report(
        from_date=three_weeks_ago,
        to_date=two_weeks_ago,
        periodics_report=mock_periodics_report,
        presubmits_report=mock_presubmits_report,
        postsubmits_report=mock_postsubmits_report,
        top_5_most_triggered_e2e_or_subsystem_jobs=[mock_identified_job_metrics_2],
        flaky_jobs=[],
    )
