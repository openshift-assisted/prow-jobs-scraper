from datetime import timedelta
from unittest.mock import MagicMock

from jobsautoreport.slack import SlackReporter


def test_send_report_should_successfully_call_slack_api_with_expected_message_format():
    test_data = {
        "success_rate": "test-success-rate",
        "number_of_jobs_triggered": 30,
        "average_jobs_duration": timedelta(minutes=30),
    }
    test_channel = "abcdefgh"
    expected_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Jobs Weekly Report",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Jobs success rate*: {test_data['success_rate']}",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Number of jobs triggered*: {test_data['number_of_jobs_triggered']}",
                }
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Average duration*:{test_data['average_jobs_duration']}",
                }
            ],
        },
    ]

    web_client_mock = MagicMock()
    web_client_mock.chat_postMessage = MagicMock()
    slack_reporter = SlackReporter(web_client=web_client_mock, channel_id=test_channel)
    slack_reporter.send_report(test_data)
    web_client_mock.chat_postMessage.assert_called_once_with(
        channel=test_channel, blocks=expected_blocks
    )
