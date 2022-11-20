import logging
from datetime import datetime

from opensearchpy import OpenSearch

from jobsautoreport import utils
from prowjobsscraper.event import JobDetails

logger = logging.getLogger(__name__)


class Querier:
    def __init__(self, opensearch_client: OpenSearch, index: str):
        self._os_client = opensearch_client
        self._index = index

    @staticmethod
    def _get_query_all_jobs(from_date: datetime, to_date: datetime) -> dict:
        return {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "job.start_time": {
                                    "gte": from_date,
                                    "lte": to_date,
                                }
                            }
                        }
                    ],
                }
            }
        }

    @staticmethod
    def _get_query_successfull_jobs(from_date: datetime, to_date: datetime) -> dict:
        return {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"job.state": "success"}},
                        {
                            "range": {
                                "job.start_time": {
                                    "gte": from_date,
                                    "lte": to_date,
                                }
                            }
                        },
                    ],
                }
            }
        }

    @staticmethod
    def _get_query_unsuccessfull_jobs(from_date: datetime, to_date: datetime) -> dict:
        return {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"job.state": "failure"}},
                        {
                            "range": {
                                "job.start_time": {
                                    "gte": from_date,
                                    "lte": to_date,
                                }
                            }
                        },
                    ],
                }
            }
        }

    def query_successfull_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        query = self._get_query_successfull_jobs(from_date, to_date)
        return self._query_and_log(query)

    def query_unsuccessfull_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        query = self._get_query_unsuccessfull_jobs(from_date, to_date)
        return self._query_and_log(query)

    def query_number_of_jobs_triggered(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        query = self._get_query_all_jobs(from_date, to_date)
        return self._query_and_log(query)

    def query_average_duration_of_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        query = self._get_query_all_jobs(from_date, to_date)
        return self._query_and_log(query)

    def _query_and_log(self, query: dict) -> list[JobDetails]:
        logger.info("OpenSearch query: %s", query)
        res = self._os_client.search(body=query, index=self._index)
        logger.info("OpenSearch response: %s", res)
        return utils.parse_jobs(res)
