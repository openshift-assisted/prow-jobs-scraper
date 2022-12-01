import logging
from typing import Any

from slack_sdk import WebClient

logger = logging.getLogger(__name__)


class SlackReporter:
    def __init__(self, web_client: WebClient, channel_id: str) -> None:
        self._client = web_client
        self._channel_id = channel_id

    def send_report(self, data: dict[str, Any]) -> None:
        if not self._is_valid(data):
            return

        blocks_list = self._format_as_message(data)
        res = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks_list
        )
        time_stamp = res["ts"]

    def comment_on_message(
        self, msg_time_stamp: str, data: list[dict[str, Any]]
    ) -> None:
        blocks_list = self._format_as_comment(data)
        res = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks_list, ts=msg_time_stamp
        )

    @staticmethod
    def _format_as_message(data: dict[str, Any]) -> list[dict[str, Any]]:
        return [
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
                        "text": f"*Jobs success rate*: {data['success_rate']}",
                    }
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Number of jobs triggered*: {data['number_of_jobs_triggered']}",
                    }
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Average duration*:{data['average_jobs_duration']}",
                    }
                ],
            },
        ]

    @staticmethod
    def _format_as_comment(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Top 10 failing e2e periodic jobs",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"1. Job name: {data[0]['name']}"},
                    {"type": "mrkdwn", "text": f"Job score: {data[0]['score']}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"2. Job name: {data[1]['name']}"},
                    {"type": "mrkdwn", "text": f"Job score: {data[1]['score']}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"3. Job name: {data[2]['name']}"},
                    {"type": "mrkdwn", "text": f"Job score: {data[2]['score']}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"4. Job name: {data[3]['name']}"},
                    {"type": "mrkdwn", "text": f"Job score: {data[3]['score']}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"5. Job name: {data[4]['name']}"},
                    {"type": "mrkdwn", "text": f"Job score: {data[4]['score']}"},
                ],
            },
        ]

    @staticmethod
    def _is_valid(data: dict[str, Any]) -> bool:
        for v in data.values():
            if v is None:
                return False
        return True
