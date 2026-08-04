import logging
from typing import Optional

from retry import retry
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from jobsautoreport.consts import (
    PERIODIC_FLAKY_JOBS_TITLE,
    TOP_5_TRIGGERED_PRESUBMIT_JOBS_TITLE,
    TOP_10_FAILED_PERIODIC_JOBS_TITLE,
    TOP_10_FAILED_POSTSUBMIT_JOBS_TITLE,
    TOP_10_FAILED_PRESUBMIT_JOBS_TITLE,
)
from jobsautoreport.models import (
    FeatureFlags,
    Report,
    SlackMessage,
    Trends,
)
from jobsautoreport.plot import Plotter
from jobsautoreport.slack.slack_generate import SlackGenerator
from jobsautoreport.trends import TrendSlackIntegrator

logger = logging.getLogger(__name__)


class SlackReporter:
    """SlackReporter sends the report the Reporter generated to a given slack channel"""

    def __init__(self, web_client: WebClient, channel_id: str) -> None:
        self._client = web_client
        self._channel_id = channel_id

    def _post_message(
        self,
        message: SlackMessage,
        thread_time_stamp: Optional[str],
    ) -> str:
        response = self._client.chat_postMessage(
            channel=self._channel_id, blocks=message, thread_ts=thread_time_stamp
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
        response = self._client.files_upload_v2(
            channel=self._channel_id,
            file=file_path,
            filename=filename,
            initial_comment=file_title,
            thread_ts=thread_time_stamp,
        )
        response.validate()
        logger.info(f"{filename} was uploaded successfully")

    def _send_success_rates(
        self,
        report: Report,
        trends: Optional[Trends],
        plotter: Plotter,
        thread_time_stamp: str,
    ) -> None:
        if report.periodics_report.success_rate is not None:
            message = SlackGenerator.create_periodic_comment(
                periodics_report=report.periodics_report
            )
            if trends is not None:
                TrendSlackIntegrator.add_periodic_trends(
                    slack_message=message, trends=trends
                )
            self._post_message(
                message=message,
                thread_time_stamp=thread_time_stamp,
            )

            # There should not be an empty graph when there are no failures
            if report.periodics_report.failures > 0:
                filename, file_path = plotter.create_most_failing_jobs_graph(
                    jobs=report.periodics_report.top_10_failing,
                    file_title=TOP_10_FAILED_PERIODIC_JOBS_TITLE,
                )
                self._upload_file(
                    file_title=TOP_10_FAILED_PERIODIC_JOBS_TITLE,
                    filename=filename,
                    file_path=file_path,
                    thread_time_stamp=thread_time_stamp,
                )

        if report.presubmits_report.success_rate is not None:
            message = SlackGenerator.create_presubmit_comment(
                presubmits_report=report.presubmits_report
            )
            if trends is not None:
                TrendSlackIntegrator.add_presubmit_trends(
                    slack_message=message, trends=trends
                )
            self._post_message(
                message=message,
                thread_time_stamp=thread_time_stamp,
            )
            if report.presubmits_report.failures > 0:
                filename, file_path = plotter.create_most_failing_jobs_graph(
                    jobs=report.presubmits_report.top_10_failing,
                    file_title=TOP_10_FAILED_PRESUBMIT_JOBS_TITLE,
                )
                self._upload_file(
                    file_title=TOP_10_FAILED_PRESUBMIT_JOBS_TITLE,
                    filename=filename,
                    file_path=file_path,
                    thread_time_stamp=thread_time_stamp,
                )
            filename, file_path = plotter.create_most_triggered_jobs_graph(
                jobs=report.top_5_most_triggered_e2e_or_subsystem_jobs,
                file_title=TOP_5_TRIGGERED_PRESUBMIT_JOBS_TITLE,
            )
            self._upload_file(
                file_title=TOP_5_TRIGGERED_PRESUBMIT_JOBS_TITLE,
                filename=filename,
                file_path=file_path,
                thread_time_stamp=thread_time_stamp,
            )

        if report.postsubmits_report.success_rate is not None:
            message = SlackGenerator.create_postsubmit_comment(
                postsubmits_report=report.postsubmits_report
            )
            if trends is not None:
                TrendSlackIntegrator.add_postsubmit_trends(
                    slack_message=message, trends=trends
                )
            self._post_message(
                message=message,
                thread_time_stamp=thread_time_stamp,
            )
            if report.postsubmits_report.failures > 0:
                filename, file_path = plotter.create_most_failing_jobs_graph(
                    jobs=report.postsubmits_report.top_10_failing,
                    file_title=TOP_10_FAILED_POSTSUBMIT_JOBS_TITLE,
                )
                self._upload_file(
                    file_title=TOP_10_FAILED_POSTSUBMIT_JOBS_TITLE,
                    filename=filename,
                    file_path=file_path,
                    thread_time_stamp=thread_time_stamp,
                )

    def _send_flakiness_rates(
        self, report: Report, plotter: Plotter, thread_time_stamp: str
    ):
        if len(report.flaky_jobs) > 0:
            filename, file_path = plotter.create_flaky_jobs_graph(
                jobs=report.flaky_jobs,
                file_title=PERIODIC_FLAKY_JOBS_TITLE,
            )
            self._upload_file(
                file_title=PERIODIC_FLAKY_JOBS_TITLE,
                filename=filename,
                file_path=file_path,
                thread_time_stamp=thread_time_stamp,
            )

    def send_report(
        self, report: Report, trends: Optional[Trends], feature_flags: FeatureFlags
    ) -> None:
        plotter = Plotter()
        thread_time_stamp = self._post_message(
            message=SlackGenerator.create_header_message(report=report),
            thread_time_stamp=None,
        )

        if feature_flags.success_rates:
            self._send_success_rates(
                report=report,
                trends=trends,
                plotter=plotter,
                thread_time_stamp=thread_time_stamp,
            )

        if feature_flags.flakiness_rates:
            self._send_flakiness_rates(
                report=report, plotter=plotter, thread_time_stamp=thread_time_stamp
            )
