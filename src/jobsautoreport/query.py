import logging
from datetime import datetime
from typing import Any

from opensearchpy import OpenSearch, helpers

from prowjobsscraper.event import JobDetails, StepEvent

logger = logging.getLogger(__name__)


class Querier:
    def __init__(
        self, opensearch_client: OpenSearch, jobs_index: str, steps_index: str
    ):
        self._os_client = opensearch_client
        self._jobs_index = jobs_index
        self._steps_index = steps_index

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

    @staticmethod
    def _get_query_steps_by_name(
        from_date: datetime, to_date: datetime, name: str
    ) -> dict[str, Any]:
        return {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "step.name": {
                                    "query": name,
                                    "operator": "and",
                                }
                            }
                        },
                        {
                            "range": {
                                "job.start_time": {
                                    "gte": from_date,
                                    "lte": to_date,
                                }
                            }
                        },
                    ]
                }
            }
        }

    def query_jobs(self, from_date: datetime, to_date: datetime) -> list[JobDetails]:
        query = self._get_query_all_jobs(from_date, to_date)
        return self._query_jobs_and_log(query)

    def query_packet_setup_step_events(
        self, from_date: datetime, to_date: datetime
    ) -> list[StepEvent]:
        query = self._get_query_steps_by_name(
            from_date, to_date, "baremetalds-packet-setup"
        )
        return self._query_step_events_and_log(query)

    def _query_jobs_and_log(self, query: dict[str, Any]) -> list[JobDetails]:
        logger.debug("OpenSearch query: %s", query)
        es_jobs = self._scan(query, self._jobs_index)
        return self._parse_jobs(es_jobs)

    def _query_step_events_and_log(self, query: dict[str, Any]) -> list[StepEvent]:
        logger.debug("OpenSearch query: %s", query)
        es_steps = self._scan(query, self._steps_index)
        return self._parse_step_events(es_steps)

    def _scan(self, query: dict[str, Any], index_name: str) -> list[dict[Any, Any]]:
        res = helpers.scan(
            client=self._os_client,
            query=query,
            index=index_name,
        )
        return list(res)

    @classmethod
    def _parse_jobs(cls, data: list[dict[Any, Any]]) -> list[JobDetails]:
        return [cls._parse_job(job["_source"]["job"]) for job in data]

    @classmethod
    def _parse_step_events(cls, data: list[dict[Any, Any]]) -> list[StepEvent]:
        return [cls._parse_step_event(step_event["_source"]) for step_event in data]

    @staticmethod
    def _parse_job(data: dict[Any, Any]) -> JobDetails:
        return JobDetails.parse_obj(data)

    @staticmethod
    def _parse_step_event(data: dict[Any, Any]) -> StepEvent:
        return StepEvent.parse_obj(data)
