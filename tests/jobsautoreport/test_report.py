from datetime import datetime, timedelta
from unittest.mock import MagicMock

from jobsautoreport.report import (
    IdentifiedJobMetrics,
    JobIdentifier,
    JobMetrics,
    Report,
    Reporter,
)
from prowjobsscraper.event import JobDetails, JobRefs, StepDetails, StepEvent

valid_queried_jobs = [
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-0",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="periodic",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-0",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="periodic",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-0",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="periodic",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-0",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="periodic",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-1",
        refs=JobRefs(base_ref="master", org="not-openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="periodic",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-1",
        refs=JobRefs(base_ref="master", org="openshift", repo="not-assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="periodic",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-2",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-2",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-2",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-2",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-2",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-subsystem-metal-assisted-3",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-subsystem-metal-assisted-3",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-subsystem-metal-assisted-3",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-e2e-metal-assisted-20",
        refs=JobRefs(base_ref="master", org="openshift", repo="not-assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="assisted-service-master-edge-metal-assisted-40",
        refs=JobRefs(base_ref="master", org="openshift", repo="not-assisted-service"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="presubmit",
        url="test",
        variant="test",
        context="edge-e2e-metal-assisted",
    ),
]

valid_queried_step_events = [
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="assisted-service-master-edge-metal-assisted-41",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-1", state="success"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="assisted-service-master-edge-metal-assisted-42",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-2", state="failure"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="assisted-service-master-edge-metal-assisted-43",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-3", state="failure"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="assisted-service-master-edge-metal-assisted-44",
            refs=JobRefs(
                base_ref="test", org="openshift", repo="non-assisted-installer"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-3", state="success"
        ),
    ),
    StepEvent(
        job=JobDetails(
            build_id="test",
            duration=2053,
            name="assisted-service-master-edge-metal-assisted-45",
            refs=JobRefs(base_ref="test", org="openshift", repo="assisted-installer"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="test",
        ),
        step=StepDetails(
            duration=456, name="baremetalds-packet-setup-4", state="success"
        ),
    ),
]

expected_report = Report(
    from_date=datetime.now(),
    to_date=datetime.now(),
    number_of_e2e_or_subsystem_periodic_jobs=4,
    number_of_successful_e2e_or_subsystem_periodic_jobs=3,
    number_of_failing_e2e_or_subsystem_periodic_jobs=1,
    success_rate_for_e2e_or_subsystem_periodic_jobs=75,
    top_10_failing_e2e_or_subsystem_periodic_jobs=[
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="assisted-service-master-edge-e2e-metal-assisted-0",
                repository="assisted-service",
                base_ref="master",
                context="edge-e2e-metal-assisted",
            ),
            metrics=JobMetrics(
                successes=3,
                failures=1,
            ),
        ),
    ],
    number_of_e2e_or_subsystem_presubmit_jobs=8,
    number_of_successful_e2e_or_subsystem_presubmit_jobs=6,
    number_of_failing_e2e_or_subsystem_presubmit_jobs=2,
    number_of_rehearsal_jobs=0,
    success_rate_for_e2e_or_subsystem_presubmit_jobs=75.0,
    top_10_failing_e2e_or_subsystem_presubmit_jobs=[
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="assisted-service-master-edge-e2e-metal-assisted-2",
                repository="assisted-service",
                base_ref="master",
                context="edge-e2e-metal-assisted",
            ),
            metrics=JobMetrics(
                successes=4,
                failures=1,
            ),
        ),
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="assisted-service-master-edge-subsystem-metal-assisted-3",
                repository="assisted-service",
                base_ref="master",
                context="edge-e2e-metal-assisted",
            ),
            metrics=JobMetrics(
                successes=2,
                failures=1,
            ),
        ),
    ],
    top_5_most_triggered_e2e_or_subsystem_jobs=[
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="assisted-service-master-edge-subsystem-metal-assisted-3",
                repository="assisted-service",
                base_ref="master",
                context="edge-e2e-metal-assisted",
            ),
            metrics=JobMetrics(
                successes=2,
                failures=1,
            ),
        ),
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="assisted-service-master-edge-e2e-metal-assisted-2",
                repository="assisted-service",
                base_ref="master",
                context="edge-e2e-metal-assisted",
            ),
            metrics=JobMetrics(
                successes=4,
                failures=1,
            ),
        ),
    ],
    number_of_successful_machine_leases=3,
    number_of_unsuccessful_machine_leases=2,
    total_number_of_machine_leased=5,
)


def test_get_report_should_successfully_create_report_from_queried_jobs():
    querier_mock = MagicMock()
    querier_mock.query_jobs = MagicMock()
    querier_mock.query_packet_setup_step_events = MagicMock()
    querier_mock.query_jobs.return_value = valid_queried_jobs
    querier_mock.query_packet_setup_step_events.return_value = valid_queried_step_events
    reporter = Reporter(querier=querier_mock)
    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)
    expected_report.from_date = a_week_ago
    expected_report.to_date = now
    report = reporter.get_report(from_date=a_week_ago, to_date=now)

    assert report == expected_report
