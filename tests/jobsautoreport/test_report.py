from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from jobsautoreport.models import JobMetrics, JobTypeMetrics, MachineMetrics
from jobsautoreport.report import IdentifiedJobMetrics, JobIdentifier, Report, Reporter
from prowjobsscraper.equinix_usages import EquinixUsage, EquinixUsageEvent
from prowjobsscraper.event import JobDetails, JobRefs, StepDetails, StepEvent


@pytest.fixture
def valid_queried_jobs() -> list[JobDetails]:
    return [
        JobDetails(
            build_id="1640330374884102144",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-0",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="periodic",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640312713374601216",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-0",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="periodic",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640312713374601216",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-0",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="periodic",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="9245358686929174623",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-0",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="periodic",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="9245312345679198765",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-0",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="periodic",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640355911056756736",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-1",
            refs=JobRefs(
                base_ref="master", org="not-openshift", repo="assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="periodic",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640353491438276608",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-1",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="not-assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="periodic",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640357441348571136",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-2",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640315275049963520",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-2",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640265230820839424",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-2",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640360574476881920",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-2",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640359635841978368",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-2",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640359588861579264",
            duration=2053,
            name="assisted-service-master-edge-subsystem-3",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="subsystem",
        ),
        JobDetails(
            build_id="1634704598183457896",
            duration=2053,
            name="assisted-service-master-edge-subsystem-3",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="subsystem",
        ),
        JobDetails(
            build_id="1640358264732389376",
            duration=2053,
            name="assisted-service-master-edge-subsystem-3",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="presubmit",
            url="test",
            variant="edge",
            context="subsystem",
        ),
        JobDetails(
            build_id="1640358264765943808",
            duration=2053,
            name="assisted-service-master-edge-e2e-metal-assisted-20",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="not-assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640358264799498240",
            duration=2053,
            name="assisted-service-master-edge-metal-assisted-40",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="not-assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640358264849829888",
            duration=2053,
            name="branch-ci-openshift-assisted-test-infra-master-images",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="postsubmit",
            url="test",
            variant="edge",
            context="images",
        ),
        JobDetails(
            build_id="1640358264887578624",
            duration=2053,
            name="branch-ci-openshift-assisted-test-infra-master-images",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="postsubmit",
            url="test",
            variant="edge",
            context="images",
        ),
        JobDetails(
            build_id="1640357442686554112",
            duration=2053,
            name="branch-ci-openshift-assisted-test-infra-master-images",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="postsubmit",
            url="test",
            variant="edge",
            context="images",
        ),
        JobDetails(
            build_id="1640357441864470528",
            duration=2053,
            name="branch-ci-openshift-assisted-test-infra-master-images",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="postsubmit",
            url="test",
            variant="edge",
            context="images",
        ),
        JobDetails(
            build_id="1640357441042386944",
            duration=2053,
            name="branch-ci-openshift-assisted-test-infra-master-images",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="postsubmit",
            url="test",
            variant="edge",
            context="images",
        ),
        JobDetails(
            build_id="1640357441063358464",
            duration=2053,
            name="branch-ci-openshift-assisted-test-infra-master-images",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="postsubmit",
            url="test",
            variant="edge",
            context="images",
        ),
        JobDetails(
            build_id="1640357441117884416",
            duration=2053,
            name="branch-ci-openshift-assisted-service-release-ocm-2.6-unit-test-postsubmit",
            refs=JobRefs(
                base_ref="release-ocm-2.6", org="openshift", repo="assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="postsubmit",
            url="test",
            variant="edge",
            context="unit-test-postsubmit",
        ),
        JobDetails(
            build_id="1634705984507088896",
            duration=2053,
            name="branch-ci-openshift-assisted-service-release-ocm-2.6-unit-test-postsubmit",
            refs=JobRefs(
                base_ref="	release-ocm-2.6", org="openshift", repo="assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="postsubmit",
            url="test",
            variant="edge",
            context="unit-test-postsubmit",
        ),
    ]


@pytest.fixture
def valid_queried_step_events() -> list[StepEvent]:
    return [
        StepEvent(
            job=JobDetails(
                build_id="1640312713341046784",
                duration=2053,
                name="assisted-service-master-edge-metal-assisted-41",
                refs=JobRefs(
                    base_ref="test", org="openshift", repo="assisted-installer"
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="success",
                type="presubmit",
                url="test",
                variant="edge",
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
                refs=JobRefs(
                    base_ref="test", org="openshift", repo="assisted-installer"
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="success",
                type="presubmit",
                url="test",
                variant="edge",
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
                refs=JobRefs(
                    base_ref="test", org="openshift", repo="assisted-installer"
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="success",
                type="presubmit",
                url="test",
                variant="edge",
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
                variant="edge",
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
                refs=JobRefs(
                    base_ref="test", org="openshift", repo="assisted-installer"
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="success",
                type="presubmit",
                url="test",
                variant="edge",
            ),
            step=StepDetails(
                duration=456, name="baremetalds-packet-setup-4", state="success"
            ),
        ),
    ]


@pytest.fixture
def valid_queried_usage_events() -> list[EquinixUsageEvent]:
    return [
        EquinixUsageEvent.create_from_equinix_usage(
            EquinixUsage(
                description=None,
                end_date="2023-03-31T23:59:59Z",
                facility="dc13",
                metro="dc",
                name="ipi-ci-op-nnk50j82-5ed26-1634705984507088896",
                plan="c3.medium.x86",
                plan_version="c3.medium.x86 v1",
                price=2,
                quantity=2,
                start_date="2023-03-01T00:00:00Z",
                total=4,
                type="Instance",
                unit="GB",
            )
        ),
        EquinixUsageEvent.create_from_equinix_usage(
            EquinixUsage(
                description=None,
                end_date="2023-03-31T23:59:59Z",
                facility="dc13",
                metro="dc",
                name="ipi-ci-op-nnk50j82-5ed26-1634704598183457896",
                plan="c3.medium.x86",
                plan_version="c3.medium.x86 v1",
                price=1,
                quantity=2,
                start_date="2023-03-01T00:00:00Z",
                total=2,
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
                plan="m3.small.x86",
                plan_version="m3.small.x86 v1",
                price=0.05,
                quantity=2,
                start_date="2023-03-01T00:00:00Z",
                total=0.1,
                type="Instance",
                unit="GB",
            )
        ),
    ]


@pytest.fixture
def expected_report() -> Report:
    return Report(
        from_date=datetime.now(),
        to_date=datetime.now(),
        number_of_e2e_or_subsystem_periodic_jobs=5,
        number_of_successful_e2e_or_subsystem_periodic_jobs=4,
        number_of_failing_e2e_or_subsystem_periodic_jobs=1,
        success_rate_for_e2e_or_subsystem_periodic_jobs=80,
        top_10_failing_e2e_or_subsystem_periodic_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="assisted-service-master-edge-e2e-metal-assisted-0",
                    repository="assisted-service",
                    base_ref="master",
                    context="e2e-metal-assisted",
                    variant="edge",
                ),
                metrics=JobMetrics(
                    successes=4, failures=1, cost=0, flakiness=0.45454545454545453
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
                    context="e2e-metal-assisted",
                    variant="edge",
                ),
                metrics=JobMetrics(
                    successes=4, failures=1, cost=0, flakiness=0.45454545454545453
                ),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="assisted-service-master-edge-subsystem-3",
                    repository="assisted-service",
                    base_ref="master",
                    context="subsystem",
                    variant="edge",
                ),
                metrics=JobMetrics(
                    successes=2, failures=1, cost=2, flakiness=0.9090909090909091
                ),
            ),
        ],
        top_5_most_triggered_e2e_or_subsystem_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="assisted-service-master-edge-subsystem-3",
                    repository="assisted-service",
                    base_ref="master",
                    context="subsystem",
                    variant="edge",
                ),
                metrics=JobMetrics(
                    successes=2, failures=1, cost=2, flakiness=0.9090909090909091
                ),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="assisted-service-master-edge-e2e-metal-assisted-2",
                    repository="assisted-service",
                    base_ref="master",
                    context="e2e-metal-assisted",
                    variant="edge",
                ),
                metrics=JobMetrics(
                    successes=4, failures=1, cost=0, flakiness=0.45454545454545453
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
                    variant="edge",
                ),
                metrics=JobMetrics(
                    successes=5, failures=1, cost=0, flakiness=0.36363636363636365
                ),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="branch-ci-openshift-assisted-service-release-ocm-2.6-unit-test-postsubmit",
                    repository="assisted-service",
                    base_ref="release-ocm-2.6",
                    context="unit-test-postsubmit",
                    variant="edge",
                ),
                metrics=JobMetrics(successes=1, failures=1, cost=4, flakiness=1),
            ),
        ],
        number_of_successful_machine_leases=3,
        number_of_unsuccessful_machine_leases=2,
        total_number_of_machine_leased=5,
        total_equinix_machines_cost=6.1,
        cost_by_machine_type=MachineMetrics(
            metrics={"c3.medium.x86": 6, "m3.small.x86": 0.1}
        ),
        cost_by_job_type=JobTypeMetrics(
            metrics={"periodic": 0, "postsubmit": 4, "presubmit": 2}
        ),
        top_5_most_expensive_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="assisted-service-master-edge-subsystem-3",
                    repository="assisted-service",
                    base_ref="master",
                    context="subsystem",
                    variant="edge",
                ),
                metrics=JobMetrics(
                    successes=2, failures=1, cost=2, flakiness=0.9090909090909091
                ),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="branch-ci-openshift-assisted-service-release-ocm-2.6-unit-test-postsubmit",
                    repository="assisted-service",
                    base_ref="release-ocm-2.6",
                    context="unit-test-postsubmit",
                    variant="edge",
                ),
                metrics=JobMetrics(successes=1, failures=1, cost=4, flakiness=1),
            ),
        ],
        flaky_jobs=[],
    )


@pytest.fixture
def querier_mock(
    valid_queried_jobs: list[JobDetails],
    valid_queried_step_events: list[StepEvent],
    valid_queried_usage_events: list[EquinixUsageEvent],
) -> MagicMock:
    querier_mock = MagicMock()
    querier_mock.query_jobs.return_value = valid_queried_jobs
    querier_mock.query_packet_setup_step_events.return_value = valid_queried_step_events
    querier_mock.query_usage_events.return_value = valid_queried_usage_events
    return querier_mock


def test_get_report_should_successfully_create_report_from_queried_jobs(
    expected_report: Report,
    querier_mock: MagicMock,
):
    reporter = Reporter(querier=querier_mock)
    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)
    expected_report.from_date = a_week_ago
    expected_report.to_date = now

    report = reporter.get_report(from_date=a_week_ago, to_date=now)

    assert report.top_5_most_expensive_jobs == expected_report.top_5_most_expensive_jobs


def test__get_flaky_jobs_with_multiple_jobs(valid_queried_jobs: list[JobDetails]):
    reporter = Reporter(querier=MagicMock())
    extra_jobs = [
        JobDetails(
            build_id="1640358264732123456",
            duration=2053,
            name="assisted-service-master-edge-subsystem-3",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="presubmit",
            url="test",
            variant="edge",
            context="subsystem",
        ),
        JobDetails(
            build_id="1640358264732654321",
            duration=2053,
            name="assisted-service-master-edge-subsystem-3",
            refs=JobRefs(base_ref="master", org="openshift", repo="assisted-service"),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="subsystem",
        ),
    ]
    jobs = valid_queried_jobs.copy() + extra_jobs

    flaky_jobs = reporter._get_flaky_jobs(jobs=jobs, usages=MagicMock())

    expected_flaky_jobs = [
        IdentifiedJobMetrics(
            job_identifier=JobIdentifier(
                name="assisted-service-master-edge-subsystem-3",
                repository="assisted-service",
                base_ref="master",
                context="subsystem",
                variant="edge",
            ),
            metrics=JobMetrics(
                successes=3, failures=2, cost=0, flakiness=0.6363636363636364
            ),
        ),
    ]

    assert len(flaky_jobs) == len(expected_flaky_jobs) == 1
    assert flaky_jobs[0].job_identifier == expected_flaky_jobs[0].job_identifier
    assert (
        pytest.approx(flaky_jobs[0].metrics.flakiness)
        == expected_flaky_jobs[0].metrics.flakiness
    )
