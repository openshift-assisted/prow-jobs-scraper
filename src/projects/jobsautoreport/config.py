import os

from projects.jobsautoreport.models import ReportInterval

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
REPORT_INTERVAL = ReportInterval(os.environ["REPORT_INTERVAL"])
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
