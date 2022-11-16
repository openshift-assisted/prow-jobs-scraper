from datetime import datetime

from opensearchpy import OpenSearch

from jobsautoreport import utils
from prowjobsscraper.event import JobDetails


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
        res_successfull_jobs = self._os_client.search(
            body=self._get_query_successfull_jobs(from_date, to_date), index=self._index
        )
        return utils.parse_jobs(res_successfull_jobs)

    def query_unsuccessfull_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        res_unsuccessfull_jobs = self._os_client.search(
            body=self._get_query_unsuccessfull_jobs(from_date, to_date),
            index=self._index,
        )

        return utils.parse_jobs(res_unsuccessfull_jobs)

    def query_number_of_jobs_triggered(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        res = self._os_client.search(
            body=self._get_query_all_jobs(from_date, to_date), index=self._index
        )
        return utils.parse_jobs(res)

    def query_average_duration_of_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        res = self._os_client.search(
            body=self._get_query_all_jobs(from_date, to_date), index=self._index
        )
        return utils.parse_jobs(res)
