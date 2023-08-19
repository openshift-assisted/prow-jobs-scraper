import os

ES_URL = os.environ["ES_URL"]
ES_USER = os.environ["ES_USER"]
ES_PASSWORD = os.environ["ES_PASSWORD"]
ES_STEP_INDEX = os.environ["ES_STEP_INDEX"]
ES_JOB_INDEX = os.environ["ES_JOB_INDEX"]
JOB_LIST_URL = os.environ["JOB_LIST_URL"]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
