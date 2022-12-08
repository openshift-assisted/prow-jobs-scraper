import logging
import sys
from datetime import datetime, timedelta

from opensearchpy import OpenSearch
from slack_sdk import WebClient

from jobsautoreport import config
from jobsautoreport.query import Querier
from jobsautoreport.report import Reporter
from jobsautoreport.slack import SlackReporter


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=config.LOG_LEVEL)

    os_usr = config.ES_USER
    os_pwd = config.ES_PASSWORD
    os_host = config.ES_URL

    client = OpenSearch(os_host, http_auth=(os_usr, os_pwd))

    index_name = config.ES_JOB_INDEX + "-*"

    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)

    querier = Querier(client, index_name)
    reporter = Reporter(querier)

    report = reporter.get_report(from_date=a_week_ago, to_date=now)

    web_client = WebClient(token=config.SLACK_BOT_TOKEN)
    slack_reporter = SlackReporter(
        web_client=web_client, channel_id=config.SLACK_CHANNEL_ID
    )
    slack_reporter.send_report(report)


if __name__ == "__main__":
    main()
