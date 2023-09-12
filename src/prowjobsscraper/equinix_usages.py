import logging
from datetime import datetime
from enum import Enum
from typing import Any, Final, Optional

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EquinixUsageIdentifier(BaseModel):
    name: str
    plan: str

    def __hash__(self) -> int:
        return hash((self.name, self.plan))

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.name == other.name
            and self.plan == self.plan
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class EquinixUsage(BaseModel):
    description: Optional[str]
    facility: str
    metro: str
    name: str
    plan: str
    plan_version: str
    price: float
    quantity: float
    total: float
    type: str
    instance: Optional[str]
    unit: str
    start_date: datetime
    end_date: Optional[datetime]

    @property
    def job_build_id(self) -> str:
        return self.name.split("-")[-1]

    def to_identifier(self) -> EquinixUsageIdentifier:
        return EquinixUsageIdentifier(name=self.name, plan=self.plan)

    def is_bandwidth_usage(self) -> bool:
        return "Bandwidth" in self.plan


class EquinixUsageEvent(BaseModel):
    class JobBuildID(BaseModel):
        build_id: str

    job: JobBuildID
    usage: EquinixUsage

    @classmethod
    def create_from_equinix_usage(cls, usage: EquinixUsage) -> "EquinixUsageEvent":
        return cls(job=cls.JobBuildID(build_id=usage.job_build_id), usage=usage)


class EquinixUsagesExtractor:
    """
    EquinixUsagesExtractor parses the Equinix usages data gathered from equinix metal API.
    """

    _EQUINIX_ENDPOINT_HEADER: Final[str] = "X-Auth-Token"
    _EQUINIX_METAL_ENDPOINT: Final[
        str
    ] = "https://api.equinix.com/metal/v1/projects/{}/usages?created[after]={}&created[before]={}"
    _USAGES_TIME_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(
        self,
        project_id: str,
        project_token: str,
        start_time: datetime,
        end_time: datetime,
    ):
        self._project_id = project_id
        self._project_token = project_token
        self._start_time = start_time
        self._end_time = end_time

    def get_project_usages(
        self,
    ) -> list[EquinixUsage]:
        equinix_project_usages = requests.get(
            url=self._EQUINIX_METAL_ENDPOINT.format(
                self._project_id,
                self._start_time.strftime(self._USAGES_TIME_FORMAT),
                self._end_time.strftime(self._USAGES_TIME_FORMAT),
            ),
            headers={self._EQUINIX_ENDPOINT_HEADER: self._project_token},
        ).json()["usages"]
        logger.info("%s usages retrieved successfully", len(equinix_project_usages))
        return self._process_usages(
            [EquinixUsage.parse_obj(usage) for usage in equinix_project_usages]
        )

    def _is_usage_in_interval(self, usage: EquinixUsage) -> bool:
        """Usage is considered to be within the time interval
        if its complete duration falls within that interval
        and it has reached completion.
        """
        return (
            usage.end_date is not None
            and usage.start_date >= self._start_time
            and usage.end_date <= self._end_time
        )

    def _process_usages(cls, usages: list[EquinixUsage]) -> list[EquinixUsage]:
        """We should index a usage if:
        - It is a non-bandwidth usage and falls within
          the designated time interval for data gathering.
        - It is a bandwidth usage and its corresponding non-bandwidth usage
          occurs within the time interval. In this situation,
          we adjust the start date and end date of the bandwidth usage to match those of its non-bandwidth counterpart.
          This ensures that they would be retrieved together in the report.
        """
        usages_should_be_indexed = []
        for usage in usages:
            if usage.is_bandwidth_usage():
                cls._change_bandwidth_usage_time_interval(
                    non_bandwidth_usage=cls._find_non_bandwidth_usage(
                        usage_name=usage.name, usages=usages
                    ),
                    bandwidth_usage=usage,
                )

            if cls._is_usage_in_interval(usage=usage):
                usages_should_be_indexed.append(usage)

        return usages_should_be_indexed

    @classmethod
    def _change_bandwidth_usage_time_interval(
        cls, non_bandwidth_usage: EquinixUsage, bandwidth_usage: EquinixUsage
    ) -> EquinixUsage:
        """Modifies the time of the bandwidth usage to match that of the non-bandwidth usage."""
        bandwidth_usage.start_date = non_bandwidth_usage.start_date
        bandwidth_usage.end_date = non_bandwidth_usage.end_date
        return bandwidth_usage

    @staticmethod
    def _find_non_bandwidth_usage(
        usage_name: str, usages: list[EquinixUsage]
    ) -> EquinixUsage:
        """Locates the non-bandwidth usage identified by the name usage_name.
        A usage is classified as bandwidth usage if its plan includes the term "Bandwidth".
        Presently, we recognize two types of bandwidth usages:
          - Outbound Bandwidth
          - Backend Transfer Bandwidth\n
        If any such usage exists, there should be a corresponding
        non-bandwidth usage associated with it.
        """
        return next(
            usage
            for usage in usages
            if usage.name == usage_name and not usage.is_bandwidth_usage()
        )
