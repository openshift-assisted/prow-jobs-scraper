from datetime import datetime
from enum import Enum
from typing import Any, NewType, Optional

from pydantic import BaseModel

from projects.prowjobsscraper.event import JobDetails


class JobType(Enum):
    PRESUBMIT = "presubmit"
    POSTSUBMIT = "postsubmit"
    PERIODIC = "periodic"
    BATCH = "batch"


class JobState(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


StepState = NewType("StepState", JobState)(JobState)


class ReportInterval(Enum):
    WEEK = "week"
    MONTH = "month"


class JobIdentifier(BaseModel):
    name: str
    repository: Optional[str]
    base_ref: Optional[str]
    context: Optional[str]
    variant: Optional[str]

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self.name == other.name

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def get_slack_name(self, display_variant: bool) -> str:
        if self.context is None or self.base_ref is None or self.repository is None:
            return self.name
        if self.variant is None or not display_variant:
            return f"{self.repository}/{self.base_ref}<br>{self.context}"
        return f"{self.repository}/{self.base_ref}<br>{self.variant}-{self.context}"

    @staticmethod
    def is_variant_unique(job_identifiers: list["JobIdentifier"]) -> bool:
        return len({job_identifier.variant for job_identifier in job_identifiers}) != 1

    @classmethod
    def create_from_job_details(cls, job_details: JobDetails) -> "JobIdentifier":
        return cls(
            name=job_details.name,
            repository=job_details.refs.repo,
            base_ref=job_details.refs.base_ref,
            context=job_details.context,
            variant=job_details.variant,
        )


class JobMetrics(BaseModel):
    successes: int
    failures: int

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def failure_rate(self) -> float:
        return 0 if self.total == 0 else (self.failures / self.total) * 100

    @property
    def success_rate(self) -> float:
        return 0 if self.total == 0 else 100 - self.failure_rate


class IdentifiedJobMetrics(BaseModel):
    job_identifier: JobIdentifier
    metrics: JobMetrics


class Report(BaseModel):
    from_date: datetime
    to_date: datetime
    number_of_e2e_or_subsystem_periodic_jobs: int
    number_of_successful_e2e_or_subsystem_periodic_jobs: int
    number_of_failing_e2e_or_subsystem_periodic_jobs: int
    success_rate_for_e2e_or_subsystem_periodic_jobs: float
    top_10_failing_e2e_or_subsystem_periodic_jobs: list[IdentifiedJobMetrics]
    number_of_e2e_or_subsystem_presubmit_jobs: int
    number_of_successful_e2e_or_subsystem_presubmit_jobs: int
    number_of_failing_e2e_or_subsystem_presubmit_jobs: int
    number_of_rehearsal_jobs: int
    success_rate_for_e2e_or_subsystem_presubmit_jobs: float
    top_10_failing_e2e_or_subsystem_presubmit_jobs: list[IdentifiedJobMetrics]
    top_5_most_triggered_e2e_or_subsystem_jobs: list[IdentifiedJobMetrics]
    number_of_postsubmit_jobs: int
    number_of_successful_postsubmit_jobs: int
    number_of_failing_postsubmit_jobs: int
    success_rate_for_postsubmit_jobs: float
    top_10_failing_postsubmit_jobs: list[IdentifiedJobMetrics]
    number_of_successful_machine_leases: int
    number_of_unsuccessful_machine_leases: int
    total_number_of_machine_leased: int
