from unittest.mock import MagicMock

from jobsautoreport.report import JobStatesCount, Report
from jobsautoreport.slack import SlackReporter


def test_send_report_should_successfully_call_slack_api_with_expected_message_format():
    report = Report(
        number_of_e2e_or_subsystem_periodic_jobs=12,
        number_of_successful_e2e_or_subsystem_periodic_jobs=9,
        number_of_failing_e2e_or_subsystem_periodic_jobs=3,
        success_rate_for_e2e_or_subsystem_periodic_jobs=75,
        top_10_failing_e2e_or_subsystem_periodic_jobs=[
            ("fake-job-1", JobStatesCount(successes=3, failures=1, failure_rate=25))
        ],
        number_of_e2e_or_subsystem_presubmit_jobs=24,
        number_of_successful_e2e_or_subsystem_presubmit_jobs=8,
        number_of_failing_e2e_or_subsystem_presubmit_jobs=16,
        number_of_rehearsal_jobs=0,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=33.33,
        top_10_failing_e2e_or_subsystem_presubmit_jobs=[
            ("fake-job-2", JobStatesCount(successes=1, failures=2, failure_rate=66.67))
        ],
        top_5_most_triggered_e2e_or_subsystem_jobs=[
            ("fake-job-2", 24),
            ("fake-job-1", 12),
        ],
        number_of_successful_machine_leases=1,
        number_of_unsuccessful_machine_leases=2,
        total_number_of_machine_leased=3,
    )

    expected_blocks_periodic = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Weekly Periodic e2e/subsystem jobs report",
                "emoji": True,
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"•\t _{report.number_of_e2e_or_subsystem_periodic_jobs}_ jobs - :slack-green: {report.number_of_successful_e2e_or_subsystem_periodic_jobs} :x: {report.number_of_failing_e2e_or_subsystem_periodic_jobs}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"•\t _{report.success_rate_for_e2e_or_subsystem_periodic_jobs}%_ succeeded",
            },
        },
    ]

    expected_blocks_presubmit = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Weekly Presubmit e2e/subsystem jobs report",
                "emoji": True,
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"•\t _{report.number_of_e2e_or_subsystem_presubmit_jobs}_ jobs - :slack-green: {report.number_of_successful_e2e_or_subsystem_presubmit_jobs} :x: {report.number_of_failing_e2e_or_subsystem_presubmit_jobs}",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"•\t _{report.number_of_rehearsal_jobs}_ rehearsal jobs triggered",
                }
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"•\t _{report.success_rate_for_e2e_or_subsystem_presubmit_jobs}%_ succeeded",
            },
        },
    ]

    expected_blocks_equinix = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Equinix",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Number of machines leased:* {report.total_number_of_machine_leased} - \n:slack-green: {report.number_of_successful_machine_leases} :x: {report.number_of_unsuccessful_machine_leases}",
                }
            ],
        },
    ]

    test_channel = "test-channel"
    test_thread_time_stamp = {"ts": "test-thread-time-stamp"}
    web_client_mock = MagicMock()
    web_client_mock.chat_postMessage = MagicMock()
    web_client_mock.files_upload = MagicMock()
    web_client_mock._create_quantity_image = MagicMock()
    web_client_mock._create_quantity_image.return_value = None
    web_client_mock._create_success_image = MagicMock()
    web_client_mock._create_success_image.return_value = None
    response_mock = MagicMock()
    response_mock.validate = MagicMock()
    response_mock.validate.return_value = True
    response_mock.__getitem__.side_effect = test_thread_time_stamp.__getitem__
    web_client_mock.chat_postMessage.return_value = response_mock
    web_client_mock.files_upload.return_value = response_mock
    slack_reporter = SlackReporter(web_client=web_client_mock, channel_id=test_channel)
    slack_reporter.send_report(report)
    web_client_mock.chat_postMessage.assert_any_call(
        channel=test_channel, blocks=expected_blocks_periodic, thread_ts=None
    )
    web_client_mock.files_upload.assert_any_call(
        channels=[test_channel],
        file="/tmp/top_10_failed_periodic_jobs.png",
        filename="top_10_failed_periodic_jobs",
        initial_comment="Top 10 Failed Periodic Jobs",
        thread_ts=None,
    )
    web_client_mock.chat_postMessage.assert_any_call(
        channel=test_channel,
        blocks=expected_blocks_presubmit,
        thread_ts=test_thread_time_stamp["ts"],
    )
    web_client_mock.files_upload.assert_any_call(
        channels=[test_channel],
        file="/tmp/top_10_failed_presubmit_jobs.png",
        filename="top_10_failed_presubmit_jobs",
        initial_comment="Top 10 Failed Presubmit Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    web_client_mock.files_upload.assert_any_call(
        channels=[test_channel],
        file="/tmp/top_5_triggered_jobs.png",
        filename="top_5_triggered_jobs",
        initial_comment="Top 5 Triggered Jobs",
        thread_ts=test_thread_time_stamp["ts"],
    )
    web_client_mock.chat_postMessage.assert_any_call(
        channel=test_channel,
        blocks=expected_blocks_equinix,
        thread_ts=test_thread_time_stamp["ts"],
    )
