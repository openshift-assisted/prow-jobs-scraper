from datetime import datetime, timedelta

from opensearchpy import OpenSearch
from slack_sdk.webhook import WebhookClient

from jobsautoreport import config
from jobsautoreport.query import Querier
from jobsautoreport.report import Reporter


def main() -> None:

    os_usr = config.ES_USER
    os_pwd = config.ES_PASSWORD
    os_host = config.ES_URL

    client = OpenSearch(os_host, http_auth=(os_usr, os_pwd))

    index_name = config.ES_JOB_INDEX + "-*"

    now = datetime.now()
    a_week_ago = now - timedelta(weeks=1)

    querier = Querier(client, index_name)
    processor = Reporter(querier)

    success_rate = processor.get_success_rate(a_week_ago, now)
    number_of_jobs_triggered = processor.get_number_of_jobs_triggered(a_week_ago, now)
    average_job_duration = processor.get_average_duration_of_jobs(a_week_ago, now)

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
                    "text": f"• Jobs success rate: _{success_rate}_\n• Number of jobs triggered: _{number_of_jobs_triggered}_\n• Jobs average duration: _{average_job_duration}_",
                },
            },
        ]
    )


if __name__ == "__main__":
    main()
