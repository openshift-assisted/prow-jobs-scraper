import os

from jobsautoreport.models import ReportInterval

ES_URL = os.environ["ES_URL"]
ES_USER = os.environ["ES_USER"]
ES_PASSWORD = os.environ["ES_PASSWORD"]
ES_JOB_INDEX = os.environ["ES_JOB_INDEX"]
ES_STEP_INDEX = os.environ["ES_STEP_INDEX"]
ES_USAGE_INDEX = os.environ["ES_USAGE_INDEX"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
REPORT_INTERVAL = ReportInterval(os.environ["REPORT_INTERVAL"])
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# feature flags

FEATURE_SUCCESS_RATES = os.environ["FEATURE_SUCCESS_RATES"]
FEATURE_EQUINIX_USAGE = os.environ["FEATURE_EQUINIX_USAGE"]
FEATURE_EQUINIX_COST = os.environ["FEATURE_EQUINIX_COST"]
FEATURE_TRENDS = os.environ["FEATURE_TRENDS"]
FEATURE_FLAKINESS_RATES = os.environ["FEATURE_FLAKINESS_RATES"]
