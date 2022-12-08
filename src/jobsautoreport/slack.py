import logging
from typing import Any

from slack_sdk import WebClient

from jobsautoreport.models import JobType
from jobsautoreport.report import Report

logger = logging.getLogger(__name__)


class SlackReporter:
    def __init__(self, web_client: WebClient, channel_id: str) -> None:
        self._client = web_client
        self._channel_id = channel_id

    def send_report(self, report: Report) -> None:
        blocks = self._format_message(report)
        logger.debug("Message format finished successfully")
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks
        )
        response.validate()
        logger.info("Message sent successfully")

        time_stamp = response["ts"]
        blocks = self._format_comment(report)
        logger.debug("comment format finished successfully")
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks, thread_ts=time_stamp
        )
        response.validate()
        logger.info("Comment sent successfully")

    @classmethod
    def _format_message(cls, report: Report) -> list[dict[str, Any]]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Periodic e2e/subsystem jobs report:",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Number of e2e/subsystem periodic jobs:* {report.number_of_e2e_or_subsystem_periodic_jobs} - \n:slack-green: {report.number_of_successful_e2e_or_subsystem_periodic_jobs} :x: {report.number_of_failing_e2e_or_subsystem_periodic_jobs}",
                    }
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Success rate for e2e/subsystem periodic jobs:* {report.success_rate_for_e2e_or_subsystem_periodic_jobs}%",
                    }
                ],
            },
            {
                "type": "section",
                "fields": cls._build_top_failing_jobs(
                    report.top_10_failing_e2e_or_subsystem_periodic_jobs,
                    JobType.PERIODIC,
                ),
            },
        ]

    @classmethod
    def _format_comment(cls, report: Report) -> list[dict[str, Any]]:
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Presubmit e2e jobs report:",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Number of e2e/subsystem presubmit jobs:* {report.number_of_e2e_or_subsystem_presubmit_jobs} - \n:slack-green: {report.number_of_successful_e2e_or_subsystem_presubmit_jobs} :x: {report.number_of_failing_e2e_or_subsystem_presubmit_jobs}",
                    }
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Number of rehearsal jobs:* {report.number_of_rehearsal_jobs}",
                    }
                ],
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Success rate for e2e/subsystem presubmit jobs:* {report.success_rate_for_e2e_or_subsystem_presubmit_jobs}%",
                    }
                ],
            },
            {
                "type": "section",
                "fields": cls._build_top_failing_jobs(
                    report.top_10_failing_e2e_or_subsystem_presubmit_jobs,
                    JobType.PRESUBMIT,
                ),
            },
            {
                "type": "section",
                "fields": cls._build_top_triggered_jobs(
                    report.top_5_most_triggered_e2e_or_subsystem_jobs
                ),
            },
        ]

    @staticmethod
    def _build_top_failing_jobs(
        top_jobs: list[tuple[str, Any]], job_type: JobType
    ) -> list[dict[str, Any]]:
        if len(top_jobs) == 0:
            return []
        res = [
            {
                "type": "mrkdwn",
                "text": f"*Top {min(10, len(top_jobs))} failed e2e/subsystem {job_type.value} jobs:*",
            }
        ]

        for job in top_jobs:
            res.append(
                {
                    "type": "mrkdwn",
                    "text": f"•\t {job[0]}: {job[1]}%",
                }
            )
        return res

    @staticmethod
    def _build_top_triggered_jobs(
        top_jobs: list[tuple[str, Any]]
    ) -> list[dict[str, Any]]:
        if len(top_jobs) == 0:
            return []
        res = [
            {
                "type": "mrkdwn",
                "text": f"*Top {min(5, len(top_jobs))} triggered e2e/subsystem jobs:*",
            }
        ]

        for job in top_jobs:
            res.append(
                {
                    "type": "mrkdwn",
                    "text": f"•\t {job[0]}:   {job[1]}",
                }
            )
        return res
