import logging
from typing import Any, Callable, Optional, Union

from retry import retry
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from jobsautoreport.plot import Plotter
from jobsautoreport.report import Report
from jobsautoreport.trends import Trends

logger = logging.getLogger(__name__)


class SlackReporter:
    """SlackReporter sends the report the Reporter generated to a given slack channel"""

    def __init__(self, web_client: WebClient, channel_id: str) -> None:
        self._client = web_client
        self._channel_id = channel_id

    def _post_message_with_trends(
        self,
        report: Report,
        trends: Trends,
        format_function: Callable[[Report, Trends], list[dict[str, Any]]],
        thread_time_stamp: Optional[str],
    ) -> str:
        blocks = format_function(report, trends)
        logger.debug("Message formatted successfully")
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks, thread_ts=thread_time_stamp
        )
        response.validate()
        logger.info("Message sent successfully")

        return response["ts"]

    def _post_message_without_trends(
        self,
        report: Report,
        format_function: Callable[[Report], list[dict[str, Any]]],
        thread_time_stamp: Optional[str],
    ) -> str:
        blocks = format_function(report)
        logger.debug("Message formatted successfully")
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=blocks, thread_ts=thread_time_stamp
        )
        response.validate()
        logger.info("Message sent successfully")

        return response["ts"]

    @retry(tries=3, delay=3, exceptions=SlackApiError, logger=logger)
    def _upload_file(
        self,
        file_title: str,
        file_path: str,
        filename: str,
        thread_time_stamp: Optional[str],
    ) -> None:
        response = self._client.files_upload(
            channels=[self._channel_id],
            file=file_path,
            filename=filename,
            initial_comment=file_title,
            thread_ts=thread_time_stamp,
        )
        response.validate()
        logger.info(f"{filename} was uploaded successfully")

    def send_report(self, report: Report, trends: Trends) -> None:
        plotter = Plotter()
        thread_time_stamp = self._post_message_without_trends(
            report=report,
            format_function=self._format_header_message,
            thread_time_stamp=None,
        )

        if report.success_rate_for_e2e_or_subsystem_periodic_jobs is not None:
            self._post_message_with_trends(
                report=report,
                trends=trends,
                format_function=self._format_periodic_comment,
                thread_time_stamp=thread_time_stamp,
            )
            # There should not be an empty graph when there are no failures
            if report.number_of_failing_e2e_or_subsystem_periodic_jobs > 0:
                filename, file_path = plotter.create_most_failing_jobs_graph(
                    jobs=report.top_10_failing_e2e_or_subsystem_periodic_jobs,
                    file_title="Top 10 Failed Periodic Jobs",
                )
                self._upload_file(
                    file_title="Top 10 Failed Periodic Jobs",
                    filename=filename,
                    file_path=file_path,
                    thread_time_stamp=thread_time_stamp,
                )

        if report.success_rate_for_e2e_or_subsystem_presubmit_jobs is not None:
            self._post_message_with_trends(
                report=report,
                trends=trends,
                format_function=self._format_presubmit_comment,
                thread_time_stamp=thread_time_stamp,
            )
            if report.number_of_failing_e2e_or_subsystem_presubmit_jobs > 0:
                filename, file_path = plotter.create_most_failing_jobs_graph(
                    jobs=report.top_10_failing_e2e_or_subsystem_presubmit_jobs,
                    file_title="Top 10 Failed Presubmit Jobs",
                )
                self._upload_file(
                    file_title="Top 10 Failed Presubmit Jobs",
                    filename=filename,
                    file_path=file_path,
                    thread_time_stamp=thread_time_stamp,
                )
            filename, file_path = plotter.create_most_triggered_jobs_graph(
                jobs=report.top_5_most_triggered_e2e_or_subsystem_jobs,
                file_title="Top 5 Triggered Presubmit Jobs",
            )
            self._upload_file(
                file_title="Top 5 Triggered Presubmit Jobs",
                filename=filename,
                file_path=file_path,
                thread_time_stamp=thread_time_stamp,
            )

        if report.success_rate_for_postsubmit_jobs is not None:
            self._post_message_with_trends(
                report=report,
                trends=trends,
                format_function=self._format_postsubmit_comment,
                thread_time_stamp=thread_time_stamp,
            )
            if report.number_of_failing_postsubmit_jobs > 0:
                filename, file_path = plotter.create_most_failing_jobs_graph(
                    jobs=report.top_10_failing_postsubmit_jobs,
                    file_title="Top 10 Failed Postsubmit Jobs",
                )
                self._upload_file(
                    file_title="Top 10 Failed Postsubmit Jobs",
                    filename=filename,
                    file_path=file_path,
                    thread_time_stamp=thread_time_stamp,
                )

        self._post_message_with_trends(
            report=report,
            trends=trends,
            format_function=self._format_equinix_message,
            thread_time_stamp=thread_time_stamp,
        )

    @staticmethod
    def _format_header_message(
        report: Report,
    ) -> list[dict[str, Any]]:
        return [
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

    def _format_periodic_comment(
        self, report: Report, trends: Trends
    ) -> list[dict[str, Any]]:
        text = (
            f"•\t _{report.number_of_e2e_or_subsystem_periodic_jobs}_ in total  {self._get_trend_phrase(trends.number_of_e2e_or_subsystem_periodic_jobs)}\n"
            f" \t\t *-* :done-circle-check: {report.number_of_successful_e2e_or_subsystem_periodic_jobs} succeeded\n"
            f" \t\t *-* :x: {report.number_of_failing_e2e_or_subsystem_periodic_jobs} failed\n"
        )

        if (
            report.success_rate_for_e2e_or_subsystem_periodic_jobs is not None
            and trends.success_rate_for_e2e_or_subsystem_periodic_jobs is not None
        ):
            text += f" \t  _{report.success_rate_for_e2e_or_subsystem_periodic_jobs:.2f}%_ *success rate*  {self._get_trend_phrase(trends.success_rate_for_e2e_or_subsystem_periodic_jobs)}\n"
        elif report.success_rate_for_e2e_or_subsystem_periodic_jobs is not None:
            text += f" \t  _{report.success_rate_for_e2e_or_subsystem_periodic_jobs:.2f}%_ *success rate*\n"

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Periodic e2e/subsystem jobs*\n",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
            },
        ]

    def _format_postsubmit_comment(
        self, report: Report, trends: Trends
    ) -> list[dict[str, Any]]:
        text = (
            f"•\t _{report.number_of_postsubmit_jobs}_ in total  {self._get_trend_phrase(trends.number_of_postsubmit_jobs)}\n"
            f" \t\t *-* :done-circle-check: {report.number_of_successful_postsubmit_jobs} succeeded\n"
            f" \t\t *-* :x: {report.number_of_failing_postsubmit_jobs} failed\n"
        )

        if (
            report.success_rate_for_postsubmit_jobs is not None
            and trends.success_rate_for_postsubmit_jobs is not None
        ):
            text += f" \t  _{report.success_rate_for_postsubmit_jobs:.2f}%_ *success rate*  {self._get_trend_phrase(trends.success_rate_for_postsubmit_jobs)}\n"
        elif report.success_rate_for_postsubmit_jobs is not None:
            text += f" \t  _{report.success_rate_for_postsubmit_jobs:.2f}%_ *success rate*\n"

        return [
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
                "text": {"type": "mrkdwn", "text": text},
            },
        ]

    def _format_presubmit_comment(
        self, report: Report, trends: Trends
    ) -> list[dict[str, Any]]:
        text = (
            f"•\t _{report.number_of_e2e_or_subsystem_presubmit_jobs}_ in total  {self._get_trend_phrase(trends.number_of_e2e_or_subsystem_presubmit_jobs)}\n"
            f" \t\t *-* :done-circle-check: {report.number_of_successful_e2e_or_subsystem_presubmit_jobs} succeeded\n"
            f" \t\t *-* :x: {report.number_of_failing_e2e_or_subsystem_presubmit_jobs} failed\n"
        )

        if (
            report.success_rate_for_e2e_or_subsystem_presubmit_jobs is not None
            and trends.success_rate_for_e2e_or_subsystem_presubmit_jobs is not None
        ):
            f"\t  _{report.success_rate_for_e2e_or_subsystem_presubmit_jobs:.2f}%_ *success rate*  {self._get_trend_phrase(trends.success_rate_for_e2e_or_subsystem_presubmit_jobs)}\n"
        elif report.success_rate_for_e2e_or_subsystem_presubmit_jobs is not None:
            text += f" \t  _{report.success_rate_for_e2e_or_subsystem_presubmit_jobs:.2f}%_ *success rate*\n"

        return [
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
                "text": {"type": "mrkdwn", "text": text},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"•\t _{report.number_of_rehearsal_jobs}_ rehearsal jobs triggered  {self._get_trend_phrase(trends.number_of_rehearsal_jobs)}",
                },
            },
        ]

    def _format_equinix_message(
        self, report: Report, trends: Trends
    ) -> list[dict[str, Any]]:
        return [
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
                        f"•\t _{report.total_number_of_machine_leased}_ machine lease attempts  {self._get_trend_phrase(trends.total_number_of_machine_leased)}\n"
                        f" \t\t *-* :done-circle-check: {report.number_of_successful_machine_leases} succeeded\n"
                        f" \t\t *-* :x: {report.number_of_unsuccessful_machine_leases} failed  {self._get_trend_phrase(trends.number_of_unsuccessful_machine_leases)}\n"
                    ),
                },
            },
        ]

    def _get_trend_phrase(self, trend: Union[float, int]) -> str:
        if trend == 0:
            return ""
        if isinstance(trend, float):
            return f"(+{trend:.2f}%)" if trend > 0 else f"({trend:.2f}%)"
        return f"(+{trend})" if trend > 0 else f"({trend})"
