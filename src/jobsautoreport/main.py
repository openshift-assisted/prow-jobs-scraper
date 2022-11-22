import logging
import sys
from datetime import datetime, timedelta

from opensearchpy import OpenSearch
from slack_sdk.webhook import WebhookClient

from jobsautoreport import config
from jobsautoreport.query import Querier
from jobsautoreport.report import Reporter


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

    success_rate = reporter.get_success_rate(a_week_ago, now)
    number_of_jobs_triggered = reporter.get_number_of_jobs_triggered(a_week_ago, now)
    average_jobs_duration = reporter.get_average_duration_of_jobs(a_week_ago, now)

    if average_jobs_duration is None:
        return

    slack_webhook_url = config.SLACK_WEBHOOK_URL
    webhook = WebhookClient(slack_webhook_url)
    res = webhook.send(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Jobs Weekly Report:*"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""
• Jobs success rate: _{success_rate}_
• Number of jobs triggered: _{number_of_jobs_triggered}_
• Jobs average duration: _{int(average_jobs_duration.total_seconds()) // 60}_ minutes, and _{int(average_jobs_duration.total_seconds())  % 60}_ seconds
""",
                },
            },
        ]
    )


if __name__ == "__main__":
    main()
