import logging
import sys
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from opensearchpy import OpenSearch
from slack_sdk import WebClient

from jobsautoreport import config
from jobsautoreport.models import FeatureFlags, ReportInterval
from jobsautoreport.query import Querier
from jobsautoreport.report import Reporter
from jobsautoreport.slack.slack_report import SlackReporter
from jobsautoreport.trends import TrendDetector


def get_reports_start_date(
    report_interval: ReportInterval, current_report_end_time: datetime
) -> tuple[datetime, datetime]:
    if report_interval == ReportInterval.WEEK:
        current_report_start_time = current_report_end_time - relativedelta(weeks=1)
        last_report_start_time = current_report_start_time - relativedelta(weeks=1)
        return current_report_start_time, last_report_start_time

    current_report_start_time = current_report_end_time - relativedelta(months=1)
    last_report_start_time = current_report_start_time - relativedelta(months=1)
    return current_report_start_time, last_report_start_time


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=config.LOG_LEVEL)

    os_usr = config.ES_USER
    os_pwd = config.ES_PASSWORD
    os_host = config.ES_URL

    client = OpenSearch(os_host, http_auth=(os_usr, os_pwd))

    now = datetime.now(tz=timezone.utc)
    if config.REPORT_INTERVAL == ReportInterval.WEEK:
        # Job execution takes 1-2 hours, and is timed out after 5. We want to have at least 6 hours for all the jobs in the report's interval to be indexed in elasticsearch
        six_hours_ago = now - relativedelta(hours=6)
        current_report_end_time = datetime(
            year=six_hours_ago.year,
            month=six_hours_ago.month,
            day=six_hours_ago.day,
            hour=six_hours_ago.hour,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )
    else:
        current_report_end_time = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )

    current_report_start_time, last_report_start_time = get_reports_start_date(
        config.REPORT_INTERVAL, current_report_end_time
    )
    last_report_end_time = current_report_start_time

    jobs_index = config.ES_JOB_INDEX + "-*"
    steps_index = config.ES_STEP_INDEX + "-*"
    usages_index = config.ES_USAGE_INDEX + "-*"

    feature_flags = FeatureFlags(
        success_rates=config.FEATURE_SUCCESS_RATES,  # type: ignore
        equinix_usage=config.FEATURE_EQUINIX_USAGE,  # type: ignore
        equinix_cost=config.FEATURE_EQUINIX_COST,  # type: ignore
        trends=config.FEATURE_TRENDS,  # type: ignore
        flakiness_rates=config.FEATURE_FLAKINESS_RATES,  # type: ignore
    )

    querier = Querier(
        opensearch_client=client,
        jobs_index=jobs_index,
        steps_index=steps_index,
        usages_index=usages_index,
    )

    reporter = Reporter(querier=querier)

    current_report = reporter.get_report(
        from_date=current_report_start_time,
        to_date=current_report_end_time,
    )
    last_report = reporter.get_report(
        from_date=last_report_start_time,
        to_date=last_report_end_time,
    )

    trends = None
    if feature_flags.trends:
        trend_detecter = TrendDetector()
        trends = trend_detecter.detect_trends(
            last_report=last_report, current_report=current_report
        )

    web_client = WebClient(token=config.SLACK_BOT_TOKEN)
    slack_reporter = SlackReporter(
        web_client=web_client, channel_id=config.SLACK_CHANNEL_ID
    )
    slack_reporter.send_report(
        report=current_report, trends=trends, feature_flags=feature_flags
    )


if __name__ == "__main__":
    main()
