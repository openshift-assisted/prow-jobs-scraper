from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from jobsautoreport.models import (
    EquinixCostReport,
    EquinixUsageReport,
    IdentifiedJobMetrics,
    JobIdentifier,
    JobMetrics,
    JobType,
    JobTypeMetrics,
    MachineMetrics,
    PeriodicJobsReport,
    PostSubmitJobsReport,
    PresubmitJobsReport,
    Report,
)
from jobsautoreport.report import Reporter
from prowjobsscraper.equinix_usages import EquinixUsage, EquinixUsageEvent
from prowjobsscraper.event import JobDetails, JobRefs, StepDetails, StepEvent


@pytest.fixture
def mock_periodic_jobs() -> list[JobDetails]:
    return [
        JobDetails(
            build_id="1640330374884102144",
            duration=2053,
            name="periodic-ci-openshift-assisted-service-release-ocm-2.6-e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
            refs=JobRefs(
                base_ref="release-ocm-2.6", org="openshift", repo="assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="periodic",
            url="test",
            context="e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
        ),
        JobDetails(
            build_id="1640312713374601216",
            duration=2053,
            name="periodic-ci-openshift-assisted-service-release-ocm-2.6-e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
            refs=JobRefs(
                base_ref="release-ocm-2.6", org="openshift", repo="assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="periodic",
            url="test",
            context="e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
        ),
        JobDetails(
            build_id="9245312345679198765",
            duration=2053,
            name="periodic-ci-openshift-assisted-service-release-ocm-2.6-e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
            refs=JobRefs(
                base_ref="release-ocm-2.6", org="openshift", repo="assisted-service"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="periodic",
            url="test",
            context="e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
        ),
        JobDetails(
            build_id="1640355911056756736",
            duration=2053,
            name="periodic-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-upgrade-agent-periodic",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="periodic",
            url="test",
            context="e2e-metal-assisted-upgrade-agent-periodic",
        ),
        JobDetails(
            build_id="1640353491438276608",
            duration=2053,
            name="periodic-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-upgrade-agent-periodic",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-test-infra"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="periodic",
            url="test",
            context="e2e-metal-assisted-upgrade-agent-periodic",
        ),
    ]


@pytest.fixture
def mock_presubmit_jobs() -> list[JobDetails]:
    return [
        JobDetails(
            build_id="1640357441348571136",
            duration=2053,
            name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-installer-agent"
            ),
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
            name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-installer-agent"
            ),
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
            name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
            refs=JobRefs(
                base_ref="master", org="openshift", repo="assisted-installer-agent"
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            variant="edge",
            context="e2e-metal-assisted",
        ),
        JobDetails(
            build_id="1640359588861579264",
            duration=2053,
            name="pull-ci-openshift-assisted-service-cloud_hotfix_releases-subsystem-aws",
            refs=JobRefs(
                base_ref="cloud_hotfix_releases",
                org="openshift",
                repo="assisted-service",
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="success",
            type="presubmit",
            url="test",
            context="subsystem-aws",
        ),
        JobDetails(
            build_id="1640358264732389376",
            duration=2053,
            name="pull-ci-openshift-assisted-service-cloud_hotfix_releases-subsystem-aws",
            refs=JobRefs(
                base_ref="cloud_hotfix_releases",
                org="openshift",
                repo="assisted-service",
            ),
            start_time=datetime.now() - timedelta(hours=1),
            state="failure",
            type="presubmit",
            url="test",
            context="subsystem-aws",
        ),
    ]


@pytest.fixture
def mock_postsubmit_jobs() -> list[JobDetails]:
    return [
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
    ]


@pytest.fixture
def mock_assisted_components_jobs(
    mock_periodic_jobs, mock_presubmit_jobs, mock_postsubmit_jobs
) -> list[JobDetails]:
    return mock_periodic_jobs + mock_presubmit_jobs + mock_postsubmit_jobs


@pytest.fixture
def mock_step_events() -> list[StepEvent]:
    return [
        StepEvent(
            job=JobDetails(
                build_id="1640315275049963520",
                duration=2053,
                name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
                refs=JobRefs(
                    base_ref="master", org="openshift", repo="assisted-installer-agent"
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="success",
                type="presubmit",
                url="test",
                variant="edge",
                context="e2e-metal-assisted",
            ),
            step=StepDetails(
                duration=456, name="baremetalds-packet-setup-1", state="success"
            ),
        ),
        StepEvent(
            job=JobDetails(
                build_id="1640357441348571136",
                duration=2053,
                name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
                refs=JobRefs(
                    base_ref="master", org="openshift", repo="assisted-installer-agent"
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="success",
                type="presubmit",
                url="test",
                variant="edge",
                context="e2e-metal-assisted",
            ),
            step=StepDetails(
                duration=456, name="baremetalds-packet-setup-2", state="failure"
            ),
        ),
        StepEvent(
            job=JobDetails(
                build_id="1640359588861579264",
                duration=2053,
                name="pull-ci-openshift-assisted-service-cloud_hotfix_releases-subsystem-aws",
                refs=JobRefs(
                    base_ref="cloud_hotfix_releases",
                    org="openshift",
                    repo="assisted-service",
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="success",
                type="presubmit",
                url="test",
                context="subsystem-aws",
            ),
            step=StepDetails(
                duration=456, name="baremetalds-packet-setup-3", state="failure"
            ),
        ),
        StepEvent(
            job=JobDetails(
                build_id="1640358264732389376",
                duration=2053,
                name="pull-ci-openshift-assisted-service-cloud_hotfix_releases-subsystem-aws",
                refs=JobRefs(
                    base_ref="cloud_hotfix_releases",
                    org="openshift",
                    repo="assisted-service",
                ),
                start_time=datetime.now() - timedelta(hours=1),
                state="failure",
                type="presubmit",
                url="test",
                context="subsystem-aws",
            ),
            step=StepDetails(
                duration=456, name="baremetalds-packet-setup-3", state="success"
            ),
        ),
    ]


@pytest.fixture
def mock_usage_events() -> list[EquinixUsageEvent]:
    return [
        EquinixUsageEvent.create_from_equinix_usage(
            EquinixUsage(
                description=None,
                end_date="2023-03-31T23:59:59Z",
                facility="dc13",
                metro="dc",
                name="ipi-ci-op-nnk50j82-5ed26-1640315275049963520",
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
                name="ipi-ci-op-nnk50j82-5ed26-1640358264732389376",
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
                name="ipi-ci-op-tb33cyhd-20a45-1640357441348571136",
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
def expected_periodic_jobs_report() -> PeriodicJobsReport:
    return PeriodicJobsReport(
        type=JobType.PERIODIC,
        total=5,
        successes=2,
        failures=3,
        success_rate=40,
        top_10_failing=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="periodic-ci-openshift-assisted-service-release-ocm-2.6-e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
                    repository="assisted-service",
                    base_ref="release-ocm-2.6",
                    context="e2e-ai-operator-ztp-sno-day2-workers-late-binding-periodic",
                ),
                metrics=JobMetrics(
                    successes=2, failures=1, cost=0, flakiness=0.9090909090909091
                ),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="periodic-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-upgrade-agent-periodic",
                    repository="assisted-test-infra",
                    base_ref="master",
                    context="e2e-metal-assisted-upgrade-agent-periodic",
                ),
                metrics=JobMetrics(successes=0, failures=2, cost=0, flakiness=0),
            ),
        ],
    )


@pytest.fixture
def expected_presubmit_jobs_report() -> PresubmitJobsReport:
    return PresubmitJobsReport(
        type=JobType.PRESUBMIT,
        total=5,
        successes=4,
        failures=1,
        success_rate=80,
        top_10_failing=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-assisted-service-cloud_hotfix_releases-subsystem-aws",
                    repository="assisted-service",
                    base_ref="cloud_hotfix_releases",
                    context="subsystem-aws",
                ),
                metrics=JobMetrics(successes=1, failures=1, cost=2, flakiness=1),
            ),
        ],
        rehearsals=0,
    )


@pytest.fixture
def expected_postsubmit_jobs_report() -> PostSubmitJobsReport:
    return PostSubmitJobsReport(
        type=JobType.POSTSUBMIT,
        total=5,
        successes=4,
        failures=1,
        success_rate=80,
        top_10_failing=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="branch-ci-openshift-assisted-test-infra-master-images",
                    repository="assisted-test-infra",
                    base_ref="master",
                    context="images",
                ),
                metrics=JobMetrics(
                    successes=3, failures=1, cost=0, flakiness=0.6060606060606061
                ),
            ),
        ],
    )


@pytest.fixture
def expected_equinix_usage_report() -> EquinixUsageReport:
    return EquinixUsageReport(
        total_machines_leased=4,
        successful_machine_leases=2,
        unsuccessful_machine_leases=2,
    )


@pytest.fixture
def expected_equinix_cost_report() -> EquinixCostReport:
    return EquinixCostReport(
        total_equinix_machines_cost=6.1,
        cost_by_machine_type=MachineMetrics(
            metrics={"c3.medium.x86": 6, "m3.small.x86": 0.1}
        ),
        cost_by_job_type=JobTypeMetrics(
            metrics={"periodic": 0, "postsubmit": 0, "presubmit": 6.1}
        ),
        top_5_most_expensive_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-assisted-service-cloud_hotfix_releases-subsystem-aws",
                    repository="assisted-service",
                    base_ref="cloud_hotfix_releases",
                    context="subsystem-aws",
                ),
                metrics=JobMetrics(successes=1, failures=1, cost=2, flakiness=1),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
                    repository="assisted-installer-agent",
                    base_ref="master",
                    context="e2e-metal-assisted",
                    variant="edge",
                ),
                metrics=JobMetrics(successes=3, failures=0, cost=4.1, flakiness=0),
            ),
        ],
    )


@pytest.fixture
def expected_report(
    expected_periodic_jobs_report: PeriodicJobsReport,
    expected_presubmit_jobs_report: PresubmitJobsReport,
    expected_postsubmit_jobs_report: PostSubmitJobsReport,
    expected_equinix_usage_report: EquinixUsageReport,
    expected_equinix_cost_report: EquinixCostReport,
) -> Report:
    return Report(
        from_date=datetime.now(),
        to_date=datetime.now(),
        periodics_report=expected_periodic_jobs_report,
        presubmits_report=expected_presubmit_jobs_report,
        postsubmits_report=expected_postsubmit_jobs_report,
        top_5_most_triggered_e2e_or_subsystem_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-assisted-service-cloud_hotfix_releases-subsystem-aws",
                    repository="assisted-service",
                    base_ref="cloud_hotfix_releases",
                    context="subsystem-aws",
                ),
                metrics=JobMetrics(successes=1, failures=1, cost=2, flakiness=1),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
                    repository="assisted-installer-agent",
                    base_ref="master",
                    context="e2e-metal-assisted",
                    variant="edge",
                ),
                metrics=JobMetrics(successes=3, failures=0, cost=4.1, flakiness=0),
            ),
        ],
        equinix_usage_report=expected_equinix_usage_report,
        equinix_cost_report=expected_equinix_cost_report,
        flaky_jobs=[],
    )


@pytest.fixture
def mock_querier(
    mock_assisted_components_jobs: list[JobDetails],
    mock_step_events: list[StepEvent],
    mock_usage_events: list[EquinixUsageEvent],
) -> MagicMock:
    mock_querier = MagicMock()
    mock_querier.query_jobs.return_value = mock_assisted_components_jobs
    mock_querier.query_packet_setup_step_events.return_value = mock_step_events
    mock_querier.query_usage_events.return_value = mock_usage_events
    return mock_querier


def test__get_periodics_report(
    mock_periodic_jobs: list[JobDetails],
    mock_usage_events: list[EquinixUsageEvent],
    expected_periodic_jobs_report: PeriodicJobsReport,
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_periodics_report(
            periodic_subsystem_and_e2e_jobs=mock_periodic_jobs,
            usages=mock_usage_events,
        )
        == expected_periodic_jobs_report
    )


def test__get_presubmits_report(
    mock_presubmit_jobs: list[JobDetails],
    mock_usage_events: list[EquinixUsageEvent],
    expected_presubmit_jobs_report: PresubmitJobsReport,
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_presubmits_report(
            presubmit_subsystem_and_e2e_jobs=mock_presubmit_jobs,
            usages=mock_usage_events,
            rehearsal_jobs=[],
        )
        == expected_presubmit_jobs_report
    )


def test__get_postsubmits_report(
    mock_postsubmit_jobs: list[JobDetails],
    mock_usage_events: list[EquinixUsageEvent],
    expected_postsubmit_jobs_report: PresubmitJobsReport,
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_postsubmits_report(
            postsubmit_jobs=mock_postsubmit_jobs,
            usages=mock_usage_events,
        )
        == expected_postsubmit_jobs_report
    )


def test__get_equinix_usage_report(
    mock_step_events: list[StepEvent], expected_equinix_usage_report: EquinixUsageReport
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_equinix_usage_report(step_events=mock_step_events)
        == expected_equinix_usage_report
    )


def test__get_equinix_cost(
    mock_assisted_components_jobs: list[JobDetails],
    mock_usage_events: list[EquinixUsageEvent],
    expected_equinix_cost_report: EquinixCostReport,
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_equinix_cost(
            assisted_components_jobs=mock_assisted_components_jobs,
            usages=mock_usage_events,
        )
        == expected_equinix_cost_report
    )


def test_get_report_should_successfully_create_report(
    expected_report: Report,
    mock_querier: MagicMock,
):
    reporter = Reporter(querier=mock_querier)
    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)
    expected_report.from_date = a_week_ago
    expected_report.to_date = now
    report = reporter.get_report(from_date=a_week_ago, to_date=now)
    assert report == expected_report
