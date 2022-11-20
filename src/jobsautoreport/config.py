import os

ES_URL = os.environ["ES_URL"]
ES_USER = os.environ["ES_USER"]
ES_PASSWORD = os.environ["ES_PASSWORD"]
ES_JOB_INDEX = os.environ["ES_JOB_INDEX"]
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
