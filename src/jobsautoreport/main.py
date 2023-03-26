import logging
import sys
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from opensearchpy import OpenSearch
from slack_sdk import WebClient

from jobsautoreport import config
from jobsautoreport.models import ReportInterval
from jobsautoreport.query import Querier
from jobsautoreport.report import Reporter
from jobsautoreport.slack import SlackReporter


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
        report_end_time = datetime(
            year=six_hours_ago.year,
            month=six_hours_ago.month,
            day=six_hours_ago.day,
            hour=six_hours_ago.hour,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )
        report_start_time = report_end_time - relativedelta(weeks=1)

    else:
        report_end_time = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )
        report_start_time = report_end_time - relativedelta(months=1)

    jobs_index = config.ES_JOB_INDEX + "-*"
    steps_index = config.ES_STEP_INDEX + "-*"
    usages_index = config.ES_USAGE_INDEX + "-*"

    querier = Querier(
        opensearch_client=client,
        jobs_index=jobs_index,
        steps_index=steps_index,
        usages_index=usages_index,
    )
    reporter = Reporter(querier=querier)

    report = reporter.get_report(from_date=report_start_time, to_date=report_end_time)

    web_client = WebClient(token=config.SLACK_BOT_TOKEN)
    slack_reporter = SlackReporter(
        web_client=web_client, channel_id=config.SLACK_CHANNEL_ID
    )
    slack_reporter.send_report(report=report)


if __name__ == "__main__":
    main()
