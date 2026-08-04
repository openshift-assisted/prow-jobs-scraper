from datetime import datetime, timedelta
from unittest.mock import MagicMock

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
from jobsautoreport.report import Reporter
from prowjobsscraper.event import JobDetails, JobRefs


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
                    successes=2, failures=1, flakiness=0.9090909090909091
                ),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="periodic-ci-openshift-assisted-test-infra-master-e2e-metal-assisted-upgrade-agent-periodic",
                    repository="assisted-test-infra",
                    base_ref="master",
                    context="e2e-metal-assisted-upgrade-agent-periodic",
                ),
                metrics=JobMetrics(successes=0, failures=2, flakiness=0),
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
                metrics=JobMetrics(successes=1, failures=1, flakiness=1),
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
                    successes=3, failures=1, flakiness=0.6060606060606061
                ),
            ),
        ],
    )


@pytest.fixture
def expected_report(
    expected_periodic_jobs_report: PeriodicJobsReport,
    expected_presubmit_jobs_report: PresubmitJobsReport,
    expected_postsubmit_jobs_report: PostSubmitJobsReport,
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
                metrics=JobMetrics(successes=1, failures=1, flakiness=1),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-assisted-installer-agent-master-edge-e2e-metal-assisted",
                    repository="assisted-installer-agent",
                    base_ref="master",
                    context="e2e-metal-assisted",
                    variant="edge",
                ),
                metrics=JobMetrics(successes=3, failures=0, flakiness=0),
            ),
        ],
        flaky_jobs=[],
    )


@pytest.fixture
def mock_querier(
    mock_assisted_components_jobs: list[JobDetails],
) -> MagicMock:
    mock_querier = MagicMock()
    mock_querier.query_jobs.return_value = mock_assisted_components_jobs
    return mock_querier


def test__get_periodics_report(
    mock_periodic_jobs: list[JobDetails],
    expected_periodic_jobs_report: PeriodicJobsReport,
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_periodics_report(
            periodic_subsystem_and_e2e_jobs=mock_periodic_jobs,
        )
        == expected_periodic_jobs_report
    )


def test__get_presubmits_report(
    mock_presubmit_jobs: list[JobDetails],
    expected_presubmit_jobs_report: PresubmitJobsReport,
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_presubmits_report(
            presubmit_subsystem_and_e2e_jobs=mock_presubmit_jobs,
            rehearsal_jobs=[],
        )
        == expected_presubmit_jobs_report
    )


def test__get_postsubmits_report(
    mock_postsubmit_jobs: list[JobDetails],
    expected_postsubmit_jobs_report: PresubmitJobsReport,
):
    reporter = Reporter(querier=MagicMock())
    assert (
        reporter._get_postsubmits_report(
            postsubmit_jobs=mock_postsubmit_jobs,
        )
        == expected_postsubmit_jobs_report
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
