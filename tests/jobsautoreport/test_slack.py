from datetime import datetime
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest

from jobsautoreport.models import JobMetrics
from jobsautoreport.report import IdentifiedJobMetrics, JobIdentifier, Report
from jobsautoreport.slack import SlackReporter
from jobsautoreport.trends import Trends


@pytest.fixture
def test_thread_time_stamp() -> dict[str, str]:
    return {"ts": "test-thread-time-stamp"}


@pytest.fixture
def slack_reporter(test_thread_time_stamp) -> SlackReporter:
    test_channel = "test-channel"
    web_client_mock = MagicMock()
    response_mock = MagicMock()
    response_mock.validate.return_value = True
    response_mock.__getitem__.side_effect = test_thread_time_stamp.__getitem__
    web_client_mock.chat_postMessage.return_value = response_mock
    web_client_mock.files_upload.return_value = response_mock

    return SlackReporter(web_client=web_client_mock, channel_id=test_channel)


@pytest.fixture
def trends() -> Trends:
    return Trends(
        number_of_e2e_or_subsystem_periodic_jobs=10,
        success_rate_for_e2e_or_subsystem_periodic_jobs=0.03,
        number_of_e2e_or_subsystem_presubmit_jobs=5,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=None,
        number_of_rehearsal_jobs=0,
        number_of_postsubmit_jobs=5,
        success_rate_for_postsubmit_jobs=-0.02,
        total_number_of_machine_leased=50,
        number_of_unsuccessful_machine_leases=-3,
    )


@pytest.fixture
def report_1() -> Report:
    return Report(
        from_date=datetime.now(),
        to_date=datetime.now(),
        number_of_e2e_or_subsystem_periodic_jobs=12,
        number_of_successful_e2e_or_subsystem_periodic_jobs=9,
        number_of_failing_e2e_or_subsystem_periodic_jobs=3,
        success_rate_for_e2e_or_subsystem_periodic_jobs=75,
        top_10_failing_e2e_or_subsystem_periodic_jobs=[
            # same variant
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-repo-branch-variant-context-1",
                    repository="repo",
                    base_ref="branch",
                    variant="variant",
                    context="context-1",
                ),
                metrics=JobMetrics(successes=3, failures=1),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-repo-branch-variant-context-2",
                    repository="repo",
                    base_ref="branch",
                    variant="variant",
                    context="context-2",
                ),
                metrics=JobMetrics(successes=3, failures=1),
            ),
        ],
        number_of_e2e_or_subsystem_presubmit_jobs=24,
        number_of_successful_e2e_or_subsystem_presubmit_jobs=8,
        number_of_failing_e2e_or_subsystem_presubmit_jobs=16,
        number_of_rehearsal_jobs=0,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=33.33,
        top_10_failing_e2e_or_subsystem_presubmit_jobs=[
            # different variant
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-repo-branch-variant-1-context-3",
                    repository="repo",
                    base_ref="branch",
                    variant="variant-1",
                    context="context-3",
                ),
                metrics=JobMetrics(successes=1, failures=2),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-repo-branch-variant-2-context-4",
                    repository="repo",
                    base_ref="branch",
                    variant="variant-2",
                    context="context-4",
                ),
                metrics=JobMetrics(successes=1, failures=2),
            ),
        ],
        top_5_most_triggered_e2e_or_subsystem_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="fake-job-2", repository="test", base_ref="test"
                ),
                metrics=JobMetrics(successes=1, failures=2),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="fake-job-1", repository="test", base_ref="test"
                ),
                metrics=JobMetrics(successes=3, failures=1),
            ),
        ],
        number_of_postsubmit_jobs=12,
        number_of_successful_postsubmit_jobs=9,
        number_of_failing_postsubmit_jobs=3,
        success_rate_for_postsubmit_jobs=75,
        top_10_failing_postsubmit_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="fake-job-3", repository="test", base_ref="test"
                ),
                metrics=JobMetrics(successes=3, failures=1),
            )
        ],
        number_of_successful_machine_leases=1,
        number_of_unsuccessful_machine_leases=2,
        total_number_of_machine_leased=3,
    )


@pytest.fixture
def report_2() -> Report:
    return Report(
        from_date=datetime.now(),
        to_date=datetime.now(),
        number_of_e2e_or_subsystem_periodic_jobs=0,
        number_of_successful_e2e_or_subsystem_periodic_jobs=0,
        number_of_failing_e2e_or_subsystem_periodic_jobs=0,
        success_rate_for_e2e_or_subsystem_periodic_jobs=None,
        top_10_failing_e2e_or_subsystem_periodic_jobs=[],
        number_of_e2e_or_subsystem_presubmit_jobs=24,
        number_of_successful_e2e_or_subsystem_presubmit_jobs=8,
        number_of_failing_e2e_or_subsystem_presubmit_jobs=16,
        number_of_rehearsal_jobs=0,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=33.33,
        top_10_failing_e2e_or_subsystem_presubmit_jobs=[
            # different variant
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-repo-branch-variant-1-context-3",
                    repository="repo",
                    base_ref="branch",
                    variant="variant-1",
                    context="context-3",
                ),
                metrics=JobMetrics(successes=1, failures=2),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="pull-ci-openshift-repo-branch-variant-2-context-4",
                    repository="repo",
                    base_ref="branch",
                    variant="variant-2",
                    context="context-4",
                ),
                metrics=JobMetrics(successes=1, failures=2),
            ),
        ],
        top_5_most_triggered_e2e_or_subsystem_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="fake-job-2", repository="test", base_ref="test"
                ),
                metrics=JobMetrics(successes=1, failures=2),
            ),
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="fake-job-1", repository="test", base_ref="test"
                ),
                metrics=JobMetrics(successes=3, failures=1),
            ),
        ],
        number_of_postsubmit_jobs=0,
        number_of_successful_postsubmit_jobs=0,
        number_of_failing_postsubmit_jobs=0,
        success_rate_for_postsubmit_jobs=None,
        top_10_failing_postsubmit_jobs=[
            IdentifiedJobMetrics(
                job_identifier=JobIdentifier(
                    name="fake-job-3", repository="test", base_ref="test"
                ),
                metrics=JobMetrics(successes=3, failures=1),
            )
        ],
        number_of_successful_machine_leases=1,
        number_of_unsuccessful_machine_leases=2,
        total_number_of_machine_leased=3,
    )


@pytest.fixture
def expected_blocks() -> Callable[[Report, Trends], dict[str, list[dict[str, Any]]]]:
    def func(report: Report, trends: Trends) -> dict[str, list[dict[str, Any]]]:
        res = {}

        res["expected_blocks_header"] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "CI Report",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{report.from_date.strftime('%Y-%m-%d %H:%M:%S')} UTC\t:arrow_right:\t{report.to_date.strftime('%Y-%m-%d %H:%M:%S')} UTC*\n",
                },
            },
        ]

        if report.success_rate_for_e2e_or_subsystem_periodic_jobs is not None:
            res["expected_blocks_periodic"] = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Periodic e2e/subsystem jobs*\n",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"•\t _{report.number_of_e2e_or_subsystem_periodic_jobs}_ in total  (+{trends.number_of_e2e_or_subsystem_periodic_jobs})\n"
                            f" \t\t *-* :done-circle-check: {report.number_of_successful_e2e_or_subsystem_periodic_jobs} succeeded\n"
                            f" \t\t *-* :x: {report.number_of_failing_e2e_or_subsystem_periodic_jobs} failed\n"
                            f" \t  _{report.success_rate_for_e2e_or_subsystem_periodic_jobs:.2f}%_ *success rate*  (+{trends.success_rate_for_e2e_or_subsystem_periodic_jobs}%)\n"
                        ),
                    },
                },
            ]

        if report.success_rate_for_e2e_or_subsystem_presubmit_jobs is not None:
            res["expected_blocks_presubmit"] = [
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Presubmit e2e/subsystem jobs*\n",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"•\t _{report.number_of_e2e_or_subsystem_presubmit_jobs}_ in total  (+{trends.number_of_e2e_or_subsystem_presubmit_jobs})\n"
                            f" \t\t *-* :done-circle-check: {report.number_of_successful_e2e_or_subsystem_presubmit_jobs} succeeded\n"
                            f" \t\t *-* :x: {report.number_of_failing_e2e_or_subsystem_presubmit_jobs} failed\n"
                            f" \t  _{report.success_rate_for_e2e_or_subsystem_presubmit_jobs:.2f}%_ *success rate*\n"
                        ),
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"•\t _{report.number_of_rehearsal_jobs}_ rehearsal jobs triggered  ",
                    },
                },
            ]

        if report.success_rate_for_postsubmit_jobs is not None:
            res["expected_blocks_postsubmit"] = [
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Postsubmit jobs*\n",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"•\t _{report.number_of_postsubmit_jobs}_ in total  (+{trends.number_of_postsubmit_jobs})\n"
                            f" \t\t *-* :done-circle-check: {report.number_of_successful_postsubmit_jobs} succeeded\n"
                            f" \t\t *-* :x: {report.number_of_failing_postsubmit_jobs} failed\n"
                            f" \t  _{report.success_rate_for_postsubmit_jobs:.2f}%_ *success rate*  ({trends.success_rate_for_postsubmit_jobs}%)\n"
                        ),
                    },
                },
            ]

        res["expected_blocks_equinix"] = [
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Equinix*",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"•\t _{report.total_number_of_machine_leased}_ machine lease attempts  (+{trends.total_number_of_machine_leased})\n"
                        f" \t\t *-* :done-circle-check: {report.number_of_successful_machine_leases} succeeded\n"
                        f" \t\t *-* :x: {report.number_of_unsuccessful_machine_leases} failed  ({trends.number_of_unsuccessful_machine_leases})\n"
                    ),
                },
            },
        ]

        return res

    return func


def test_send_report_should_successfully_call_slack_api_with_expected_message_format(
    report_1: Report,
    expected_blocks: Callable[[Report, Trends], dict[str, list[dict[str, Any]]]],
    test_thread_time_stamp: dict[str, str],
    trends: Trends,
    slack_reporter: SlackReporter,
):
    blocks = expected_blocks(report_1, trends)
    slack_reporter.send_report(report_1, trends)

    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_header"],
        thread_ts=None,
    )
    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_periodic"],
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.files_upload.assert_any_call(
        channels=[slack_reporter._channel_id],
        file="/tmp/top_10_failed_periodic_jobs.png",
        filename="top_10_failed_periodic_jobs",
        initial_comment="Top 10 Failed Periodic Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_presubmit"],
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.files_upload.assert_any_call(
        channels=[slack_reporter._channel_id],
        file="/tmp/top_10_failed_presubmit_jobs.png",
        filename="top_10_failed_presubmit_jobs",
        initial_comment="Top 10 Failed Presubmit Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.files_upload.assert_any_call(
        channels=[slack_reporter._channel_id],
        file="/tmp/top_5_triggered_presubmit_jobs.png",
        filename="top_5_triggered_presubmit_jobs",
        initial_comment="Top 5 Triggered Presubmit Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_postsubmit"],
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.files_upload.assert_any_call(
        channels=[slack_reporter._channel_id],
        file="/tmp/top_10_failed_postsubmit_jobs.png",
        filename="top_10_failed_postsubmit_jobs",
        initial_comment="Top 10 Failed Postsubmit Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_equinix"],
        thread_ts=test_thread_time_stamp["ts"],
    )


def test_send_report_should_successfully_call_slack_api_with_filtering_none_success_rates(
    report_2: Report,
    expected_blocks: Callable[[Report, Trends], dict[str, list[dict[str, Any]]]],
    test_thread_time_stamp: dict[str, str],
    trends: Trends,
    slack_reporter: SlackReporter,
):
    blocks = expected_blocks(report_2, trends)
    slack_reporter.send_report(report_2, trends)

    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_header"],
        thread_ts=None,
    )
    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_presubmit"],
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.files_upload.assert_any_call(
        channels=[slack_reporter._channel_id],
        file="/tmp/top_10_failed_presubmit_jobs.png",
        filename="top_10_failed_presubmit_jobs",
        initial_comment="Top 10 Failed Presubmit Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.files_upload.assert_any_call(
        channels=[slack_reporter._channel_id],
        file="/tmp/top_5_triggered_presubmit_jobs.png",
        filename="top_5_triggered_presubmit_jobs",
        initial_comment="Top 5 Triggered Presubmit Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    slack_reporter._client.chat_postMessage.assert_any_call(
        channel=slack_reporter._channel_id,
        blocks=blocks["expected_blocks_equinix"],
        thread_ts=test_thread_time_stamp["ts"],
    )


def test_JobIdentifier_short_names_in_slack(report_1):
    expected_top_10_failing_e2e_or_subsystem_periodic_jobs_slack_names = [
        "repo/branch<br>context-1",
        "repo/branch<br>context-2",
    ]

    expected_top_10_failing_e2e_or_subsystem_presubmit_jobs_slack_names = [
        "repo/branch<br>variant-1-context-3",
        "repo/branch<br>variant-2-context-4",
    ]

    top_failing_periodics = report_1.top_10_failing_e2e_or_subsystem_periodic_jobs
    is_unique_variant_periodics = JobIdentifier.is_variant_unique(
        [identified_job.job_identifier for identified_job in top_failing_periodics]
    )
    slack_names_periodics = [
        job.job_identifier.get_slack_name(is_unique_variant_periodics)
        for job in top_failing_periodics
    ]
    top_failing_presubmits = report_1.top_10_failing_e2e_or_subsystem_presubmit_jobs
    is_unique_variant_presubmits = JobIdentifier.is_variant_unique(
        [identified_job.job_identifier for identified_job in top_failing_presubmits]
    )
    slack_names_presubmits = [
        job.job_identifier.get_slack_name(is_unique_variant_presubmits)
        for job in top_failing_presubmits
    ]

    assert (
        slack_names_periodics
        == expected_top_10_failing_e2e_or_subsystem_periodic_jobs_slack_names
    )
    assert (
        slack_names_presubmits
        == expected_top_10_failing_e2e_or_subsystem_presubmit_jobs_slack_names
    )


def test_get_trend_phrase():
    slack_reporter = SlackReporter(web_client=MagicMock(), channel_id=MagicMock())
    assert slack_reporter._get_trend_phrase(trend=1) == "(+1)"
    assert slack_reporter._get_trend_phrase(trend=0) == ""
    assert slack_reporter._get_trend_phrase(trend=-1) == "(-1)"
