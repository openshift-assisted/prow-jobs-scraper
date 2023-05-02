import logging
from typing import Any, Callable, Optional

from retry import retry
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from jobsautoreport.models import JobTypeMetrics, MachineMetrics
from jobsautoreport.plot import Plotter
from jobsautoreport.report import Report

logger = logging.getLogger(__name__)


class SlackReporter:
    """SlackReporter sends the report the Reporter generated to a given slack channel"""

    def __init__(self, web_client: WebClient, channel_id: str) -> None:
        self._client = web_client
        self._channel_id = channel_id

    def _post_message(
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

    def send_report(self, report: Report) -> None:
        plotter = Plotter()
        thread_time_stamp = self._post_message(
            report=report,
            format_function=self._format_header_message,
            thread_time_stamp=None,
        )

        if report.success_rate_for_e2e_or_subsystem_periodic_jobs is not None:
            self._post_message(
                report=report,
                format_function=self._format_periodic_comment,
                thread_time_stamp=thread_time_stamp,
            )
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
            self._post_message(
                report=report,
                format_function=self._format_presubmit_comment,
                thread_time_stamp=thread_time_stamp,
            )
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
            self._post_message(
                report=report,
                format_function=self._format_postsubmit_comment,
                thread_time_stamp=thread_time_stamp,
            )
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

        if report.total_equinix_machines_cost > 0:
            self._post_message(
                report=report,
                format_function=self._format_equinix_message,
                thread_time_stamp=thread_time_stamp,
            )
            filename, file_path = plotter.create_most_expensive_jobs_graph(
                jobs=report.top_5_most_expensive_jobs,
                file_title="Top 5 Most Expensive Jobs",
            )
            self._upload_file(
                file_title="Top 5 Most Expensive Jobs",
                filename=filename,
                file_path=file_path,
                thread_time_stamp=thread_time_stamp,
            )

    @staticmethod
    def _format_header_message(report: Report) -> list[dict[str, Any]]:
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

    @staticmethod
    def _format_periodic_comment(report: Report) -> list[dict[str, Any]]:
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
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"•\t _{report.number_of_e2e_or_subsystem_periodic_jobs}_ in total\n"
                        f" \t\t *-* :done-circle-check: {report.number_of_successful_e2e_or_subsystem_periodic_jobs} succeeded\n"
                        f" \t\t *-* :x: {report.number_of_failing_e2e_or_subsystem_periodic_jobs} failed\n"
                        f" \t  _{report.success_rate_for_e2e_or_subsystem_periodic_jobs:.2f}%_ *success rate*\n"
                    ),
                },
            },
        ]

    @staticmethod
    def _format_postsubmit_comment(report: Report) -> list[dict[str, Any]]:
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
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"•\t _{report.number_of_postsubmit_jobs}_ in total\n"
                        f" \t\t *-* :done-circle-check: {report.number_of_successful_postsubmit_jobs} succeeded\n"
                        f" \t\t *-* :x: {report.number_of_failing_postsubmit_jobs} failed\n"
                        f" \t  _{report.success_rate_for_postsubmit_jobs:.2f}%_ *success rate*\n"
                    ),
                },
            },
        ]

    @staticmethod
    def _format_presubmit_comment(report: Report) -> list[dict[str, Any]]:
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
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"•\t _{report.number_of_e2e_or_subsystem_presubmit_jobs}_ in total\n"
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
                    "text": f"•\t _{report.number_of_rehearsal_jobs}_ rehearsal jobs triggered",
                },
            },
        ]

    @classmethod
    def _format_equinix_message(cls, report: Report) -> list[dict[str, Any]]:
        equinix_message: list[dict[str, Any]] = [
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
                        f"•\t _{report.total_number_of_machine_leased}_ machine lease attempts\n"
                        f" \t\t *-* :done-circle-check: {report.number_of_successful_machine_leases} succeeded\n"
                        f" \t\t *-* :x: {report.number_of_unsuccessful_machine_leases} failed\n"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"•\t Total cost: *_{int(report.total_equinix_machines_cost)}_ $*  ",
                },
            },
        ]

        cls._create_cost_by_machine_type_section(
            equinix_message, report.cost_by_machine_type
        )
        cls._create_cost_by_job_type_section(equinix_message, report.cost_by_job_type)

        return equinix_message

    @staticmethod
    def _create_cost_by_machine_type_section(
        equinix_message: list[dict[str, Any]], machine_metrics: MachineMetrics
    ):
        if machine_metrics.is_zero():
            return

        new_section: dict[str, Any] = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (f"•\t Cost by machine type:\n"),
            },
        }

        for machine_type, cost in machine_metrics.metrics.items():
            if "Bandwidth" not in machine_type and int(cost) > 0:
                formatted_machine_type = machine_type.replace(".", " ")
                new_section["text"]["text"] = (
                    new_section["text"]["text"]
                    + f" \t\t *-* {formatted_machine_type}: *_{int(cost)}_ $*\n"
                )

        equinix_message.append(new_section)

    @staticmethod
    def _create_cost_by_job_type_section(
        equinix_message: list[dict[str, Any]], job_type_metrics: JobTypeMetrics
    ):
        if job_type_metrics.is_zero():
            return

        new_section: dict[str, Any] = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (f"•\t Cost by job type:\n"),
            },
        }

        for job_type, cost in job_type_metrics.dict().items():
            if int(cost) > 0:
                new_section["text"]["text"] = (
                    new_section["text"]["text"]
                    + f" \t\t *-* {job_type}: *_{int(cost)}_ $*\n"
                )

        equinix_message.append(new_section)
