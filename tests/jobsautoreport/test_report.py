from datetime import datetime, timedelta
from unittest.mock import MagicMock

from jobsautoreport.report import (
    IdentifiedJobMetrics,
    JobIdentifier,
    JobMetrics,
    Report,
    Reporter,
)
from prowjobsscraper.equinix_usages import EquinixUsage, EquinixUsageEvent
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
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-test-infra-master-images",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-test-infra"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="postsubmit",
        url="test",
        variant="test",
        context="images",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-test-infra-master-images",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-test-infra"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="postsubmit",
        url="test",
        variant="test",
        context="images",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-test-infra-master-images",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-test-infra"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="postsubmit",
        url="test",
        variant="test",
        context="images",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-test-infra-master-images",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-test-infra"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="postsubmit",
        url="test",
        variant="test",
        context="images",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-test-infra-master-images",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-test-infra"),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="postsubmit",
        url="test",
        variant="test",
        context="images",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-test-infra-master-images",
        refs=JobRefs(base_ref="master", org="openshift", repo="assisted-test-infra"),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="postsubmit",
        url="test",
        variant="test",
        context="images",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-service-release-ocm-2.6-unit-test-postsubmit",
        refs=JobRefs(
            base_ref="release-ocm-2.6", org="openshift", repo="assisted-service"
        ),
        start_time=datetime.now() - timedelta(hours=1),
        state="success",
        type="postsubmit",
        url="test",
        variant="test",
        context="unit-test-postsubmit",
    ),
    JobDetails(
        build_id="test",
        duration=2053,
        name="branch-ci-openshift-assisted-service-release-ocm-2.6-unit-test-postsubmit",
        refs=JobRefs(
            base_ref="	release-ocm-2.6", org="openshift", repo="assisted-service"
        ),
        start_time=datetime.now() - timedelta(hours=1),
        state="failure",
        type="postsubmit",
        url="test",
        variant="test",
        context="unit-test-postsubmit",
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

valid_queried_usage_events = [
    EquinixUsageEvent.create_from_equinix_usage(
        EquinixUsage(
            description=None,
            end_date="2023-03-31T23:59:59Z",
            facility="dc13",
            metro="dc",
            name="ipi-ci-op-nnk50j82-5ed26-1634705984507088896",
            plan="Outbound Bandwidth",
            plan_version="Outbound Bandwidth",
            price=0.05,
            quantity=2,
            start_date="2023-03-01T00:00:00Z",
            total=0.1,
            type="Instance",
            unit="GB",
        )
    ),
    EquinixUsageEvent.create_from_equinix_usage(
        usage=EquinixUsage(
            description=None,
            end_date="2023-03-31T23:59:59Z",
            facility="dc13",
            metro="dc",
            name="ipi-ci-op-tb33cyhd-20a45-1638140834400440320",
            plan="Outbound Bandwidth",
            plan_version="Outbound Bandwidth",
            price=0.05,
            quantity=2,
            start_date="2023-03-01T00:00:00Z",
            total=0.1,
            type="Instance",
            unit="GB",
        )
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
                variant="test",
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
                variant="test",
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
                variant="test",
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
                variant="test",
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
                variant="test",
            ),
            metrics=JobMetrics(
                successes=4,
                failures=1,
            ),
        ),
    ],
    number_of_postsubmit_jobs=8,
    number_of_successful_postsubmit_jobs=6,
    number_of_failing_postsubmit_jobs=2,
    success_rate_for_postsubmit_jobs=75.0,
    top_10_failing_postsubmit_jobs=[
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="branch-ci-openshift-assisted-test-infra-master-images",
                repository="assisted-test-infra",
                base_ref="master",
                context="images",
                variant="test",
            ),
            metrics=JobMetrics(
                successes=5,
                failures=1,
            ),
        ),
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="branch-ci-openshift-assisted-service-release-ocm-2.6-unit-test-postsubmit",
                repository="assisted-service",
                base_ref="release-ocm-2.6",
                context="unit-test-postsubmit",
                variant="test",
            ),
            metrics=JobMetrics(
                successes=1,
                failures=1,
            ),
        ),
    ],
    number_of_successful_machine_leases=3,
    number_of_unsuccessful_machine_leases=2,
    total_number_of_machine_leased=5,
    total_equinix_machines_cost=0.2,
)


def test_get_report_should_successfully_create_report_from_queried_jobs():
    querier_mock = MagicMock()
    querier_mock.query_jobs.return_value = valid_queried_jobs
    querier_mock.query_packet_setup_step_events.return_value = valid_queried_step_events
    querier_mock.query_usage_events.return_value = valid_queried_usage_events
    reporter = Reporter(querier=querier_mock)
    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)
    expected_report.from_date = a_week_ago
    expected_report.to_date = now

    report = reporter.get_report(from_date=a_week_ago, to_date=now)

    assert report == expected_report
