import logging
from datetime import datetime
from typing import Any

from opensearchpy import OpenSearch, helpers

from prowjobsscraper.equinix_usages import EquinixUsageEvent
from prowjobsscraper.event import JobDetails, StepEvent

logger = logging.getLogger(__name__)


class Querier:
    def __init__(
        self,
        opensearch_client: OpenSearch,
        jobs_index: str,
        steps_index: str,
        usages_index: str,
    ):
        self._os_client = opensearch_client
        self._jobs_index = jobs_index
        self._steps_index = steps_index
        self._usages_index = usages_index

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

    @staticmethod
    def _get_query_usages(from_date: datetime, to_date: datetime) -> dict[str, Any]:
        return {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "usage.start_date": {
                                    "gte": from_date,
                                    "lte": to_date,
                                }
                            }
                        }
                    ]
                }
            }
        }

    def query_jobs(self, from_date: datetime, to_date: datetime) -> list[JobDetails]:
        query = self._get_query_all_jobs(from_date=from_date, to_date=to_date)
        return self._query_jobs_and_log(query=query)

    def query_packet_setup_step_events(
        self, from_date: datetime, to_date: datetime
    ) -> list[StepEvent]:
        query = self._get_query_steps_by_name(
            from_date=from_date, to_date=to_date, name="baremetalds-packet-setup"
        )
        return self._query_step_events_and_log(query=query)

    def query_usage_events(
        self, from_date: datetime, to_date: datetime
    ) -> list[EquinixUsageEvent]:
        query = self._get_query_usages(from_date=from_date, to_date=to_date)
        return self._query_usage_events_and_log(query=query)

    def _query_jobs_and_log(self, query: dict[str, Any]) -> list[JobDetails]:
        logger.debug("OpenSearch query: %s", query)
        elastic_search_jobs = self._scan(query=query, index_name=self._jobs_index)
        return self._parse_jobs(elastic_search_jobs=elastic_search_jobs)

    def _query_step_events_and_log(self, query: dict[str, Any]) -> list[StepEvent]:
        logger.debug("OpenSearch query: %s", query)
        elastic_search_steps = self._scan(query=query, index_name=self._steps_index)
        return self._parse_step_events(elastic_search_steps=elastic_search_steps)

    def _query_usage_events_and_log(
        self, query: dict[str, Any]
    ) -> list[EquinixUsageEvent]:
        logger.debug("OpenSearch query: %s", query)
        elastic_search_usages = self._scan(query=query, index_name=self._usages_index)
        return self._parse_usage_events(elastic_search_usages=elastic_search_usages)

    def _scan(self, query: dict[str, Any], index_name: str) -> list[dict[Any, Any]]:
        res = helpers.scan(
            client=self._os_client,
            query=query,
            index=index_name,
        )
        return list(res)

    def _parse_jobs(
        self, elastic_search_jobs: list[dict[Any, Any]]
    ) -> list[JobDetails]:
        return [self._parse_job(job["_source"]["job"]) for job in elastic_search_jobs]

    def _parse_step_events(
        self, elastic_search_steps: list[dict[Any, Any]]
    ) -> list[StepEvent]:
        return [
            self._parse_step_event(step_event["_source"])
            for step_event in elastic_search_steps
        ]

    def _parse_usage_events(
        self, elastic_search_usages: list[dict[Any, Any]]
    ) -> list[EquinixUsageEvent]:
        return [
            self._parse_usage_event(usage_event["_source"])
            for usage_event in elastic_search_usages
        ]

    @staticmethod
    def _parse_job(elastic_search_job: dict[Any, Any]) -> JobDetails:
        return JobDetails.parse_obj(elastic_search_job)

    @staticmethod
    def _parse_step_event(elastic_search_step: dict[Any, Any]) -> StepEvent:
        return StepEvent.parse_obj(elastic_search_step)

    @staticmethod
    def _parse_usage_event(elastic_search_usage: dict[Any, Any]) -> EquinixUsageEvent:
        return EquinixUsageEvent.parse_obj(elastic_search_usage)
