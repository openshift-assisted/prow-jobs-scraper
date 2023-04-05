import logging
from datetime import datetime
from enum import Enum
from typing import Final, Optional

import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class EquinixUsagesScrapeInterval(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


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
        return [EquinixUsage.parse_obj(usage) for usage in equinix_project_usages]
