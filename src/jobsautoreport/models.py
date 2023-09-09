from datetime import datetime
from enum import Enum
from typing import Any, NewType, Optional

from pydantic import BaseModel

from prowjobsscraper.event import JobDetails


class JobType(Enum):
    PRESUBMIT = "presubmit"
    POSTSUBMIT = "postsubmit"
    PERIODIC = "periodic"
    BATCH = "batch"


class JobState(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class ReportInterval(Enum):
    WEEK = "week"
    MONTH = "month"


class Metric(BaseModel):
    def is_zero(self) -> bool:
        for cost in self.dict().values():
            if cost > 0:
                return False
        return True


class MachineMetrics(Metric):
    metrics: dict[str, float]

    def is_zero(self) -> bool:
        return sum(self.metrics.values()) == 0


class JobTypeMetrics(Metric):
    metrics: dict[str, float]

    def is_zero(self) -> bool:
        return sum(self.metrics.values()) == 0


class JobMetrics(Metric):
    successes: int
    failures: int
    cost: float
    flakiness: Optional[float]
    flakiness_threshold: float = 0.5

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def failure_rate(self) -> Optional[float]:
        return None if self.total == 0 else (self.failures / self.total) * 100

    @property
    def success_rate(self) -> Optional[float]:
        return None if self.failure_rate is None else 100 - self.failure_rate

    def is_flaky(self) -> Optional[bool]:
        return (
            self.flakiness > self.flakiness_threshold and self.total >= 5
            if self.flakiness is not None
            else None
        )


class FeatureFlags(BaseModel):
    success_rates: bool
    equinix_usage: bool
    equinix_cost: bool
    trends: bool
    flakiness_rates: bool


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
        if self.context is None:
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


class IdentifiedJobMetrics(BaseModel):
    job_identifier: JobIdentifier
    metrics: JobMetrics


class EndToEndOrSubsystemJobsReport(BaseModel):
    type: JobType
    total: int
    successes: int
    failures: int
    success_rate: Optional[float]
    top_10_failing: list[IdentifiedJobMetrics]


class PeriodicJobsReport(EndToEndOrSubsystemJobsReport):
    pass


class PresubmitJobsReport(EndToEndOrSubsystemJobsReport):
    rehearsals: int


class PostSubmitJobsReport(EndToEndOrSubsystemJobsReport):
    pass


class EquinixUsageReport(BaseModel):
    total_machines_leased: int
    successful_machine_leases: int
    unsuccessful_machine_leases: int


class EquinixCostReport(BaseModel):
    total_equinix_machines_cost: float
    cost_by_machine_type: MachineMetrics
    cost_by_job_type: JobTypeMetrics
    top_5_most_expensive_jobs: list[IdentifiedJobMetrics]


class Report(BaseModel):
    from_date: datetime
    to_date: datetime
    periodics_report: PeriodicJobsReport
    presubmits_report: PresubmitJobsReport
    postsubmits_report: PostSubmitJobsReport
    top_5_most_triggered_e2e_or_subsystem_jobs: list[IdentifiedJobMetrics]
    equinix_usage_report: EquinixUsageReport
    equinix_cost_report: EquinixCostReport
    flaky_jobs: list[IdentifiedJobMetrics]


class Trends(BaseModel):
    number_of_e2e_or_subsystem_periodic_jobs: int
    success_rate_for_e2e_or_subsystem_periodic_jobs: Optional[float] = None
    number_of_e2e_or_subsystem_presubmit_jobs: int
    success_rate_for_e2e_or_subsystem_presubmit_jobs: Optional[float] = None
    number_of_rehearsal_jobs: int
    number_of_postsubmit_jobs: int
    success_rate_for_postsubmit_jobs: Optional[float] = None
    total_number_of_machine_leased: int
    number_of_unsuccessful_machine_leases: int
    total_equinix_machines_cost: float


StepState = NewType("StepState", JobState)(JobState)


SlackMessage = list[dict[str, Any]]
