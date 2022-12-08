import logging
from datetime import datetime
from typing import Any

from opensearchpy import OpenSearch, helpers

from jobsautoreport import utils
from jobsautoreport.models import JobState, JobType
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
                    ]
                }
            }
        }

    def query_all_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> list[JobDetails]:
        query = self._get_query_all_jobs(from_date, to_date)
        return self._query_and_log(query)

    def _query_and_log(self, query: dict) -> list[JobDetails]:
        logger.debug("OpenSearch query: %s", query)
        jobs = self._scan(query)
        return utils.parse_jobs(jobs)

    def _scan(self, query: dict[str, Any]) -> list[dict[Any, Any]]:
        res = helpers.scan(
            client=self._os_client,
            query=query,
            index=self._index,
        )
        return list(res)
