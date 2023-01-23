import logging
from datetime import datetime
from typing import Any, Callable, Optional

from pydantic import BaseModel

from jobsautoreport.models import JobState, JobType, StepState
from jobsautoreport.query import Querier
from prowjobsscraper.event import JobDetails

logger = logging.getLogger(__name__)


class JobIdentifier(BaseModel):

    name: str
    repository: str
    base_ref: str
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

    def __str__(self) -> str:
        return (
            f"successes: {self.successes}\n"
            f"failures: {self.failures}\n"
            f"success_rate: {self.success_rate}\n"
            f"failure_rate: {self.failure_rate}\n"
            f"total: {self.total}\n"
        )


class IdentifiedJobMetrics(BaseModel):

    job_identifier: JobIdentifier
    metrics: JobMetrics

    def __str__(self) -> str:
        return (
            f"job name: {self.job_identifier.name}"
            f"successes: {self.metrics.successes}\n"
            f"failures: {self.metrics.failures}\n"
            f"success_rate: {self.metrics.success_rate}\n"
            f"failure_rate: {self.metrics.failure_rate}\n"
            f"total: {self.metrics.total}\n"
        )


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

    def __str__(self) -> str:
        return (
            f"from {self.from_date} to {self.to_date}:\n"
            f"number_of_e2e_or_subsystem_periodic_jobs_triggered: {self.number_of_e2e_or_subsystem_periodic_jobs}\n"
            f"number_of_successful_e2e_or_subsystem_periodic_jobs_triggered: {self.number_of_successful_e2e_or_subsystem_periodic_jobs}\n"
            f"number_of_failures_e2e_or_subsystem_periodic_jobs_triggered: {self.number_of_failing_e2e_or_subsystem_periodic_jobs}\n"
            f"success_rate_for_e2e_or_subsystem_periodic_jobs: {self.success_rate_for_e2e_or_subsystem_periodic_jobs}\n"
            f"top_10_failed_e2e_or_subsystem_periodic_jobs: {self.top_10_failing_e2e_or_subsystem_periodic_jobs}\n"
            f"number_of_e2e_or_subsystem_presubmit_jobs_triggered: {self.number_of_e2e_or_subsystem_presubmit_jobs}\n"
            f"number_of_successful_e2e_or_subsystem_presubmit_jobs_triggered: {self.number_of_successful_e2e_or_subsystem_presubmit_jobs}\n"
            f"number_of_failures_e2e_or_subsystem_pre_submit_jobs_triggered: {self.number_of_failing_e2e_or_subsystem_presubmit_jobs}\n"
            f"number_of_rehearsal_jobs_triggered: {self.number_of_rehearsal_jobs}\n"
            f"success_rate_for_e2e_or_subsystem_presubmit_jobs: {self.success_rate_for_e2e_or_subsystem_presubmit_jobs}\n"
            f"top_10_failed_e2e_or_subsystem_presubmit_jobs: {self.top_10_failing_e2e_or_subsystem_presubmit_jobs}\n"
            f"top_5_most_triggered_e2e_or_subsystem_jobs: {self.top_5_most_triggered_e2e_or_subsystem_jobs}\n"
            f"number_of_postsubmit_jobs_triggered: {self.number_of_postsubmit_jobs}\n"
            f"number_of_successful_postsubmit_jobs_triggered: {self.number_of_successful_postsubmit_jobs}\n"
            f"number_of_failures_postsubmit_jobs_triggered: {self.number_of_failing_postsubmit_jobs}\n"
            f"success_rate_for_postsubmit_jobs: {self.success_rate_for_postsubmit_jobs}\n"
            f"top_10_failed_postsubmit_jobs: {self.top_10_failing_postsubmit_jobs}\n"
            f"number_of_successful_machine_leases: {self.number_of_successful_machine_leases}\n"
            f"number_of_unsuccessful_machine_leases: {self.number_of_unsuccessful_machine_leases}\n"
            f"total_number_of_machine_leased: {self.total_number_of_machine_leased}\n"
        )


class Reporter:
    def __init__(self, querier: Querier):
        self._querier = querier

    @staticmethod
    def _get_job_triggers_count(job_name: str, jobs: list[JobDetails]) -> int:
        return sum(1 for job in jobs if job.name == job_name)

    @staticmethod
    def _get_number_of_jobs_by_state(
        jobs: list[JobDetails], job_state: JobState
    ) -> int:
        return len([job for job in jobs if job.state == job_state.value])

    def _get_job_metrics(
        self, job_identifier: JobIdentifier, jobs: list[JobDetails]
    ) -> IdentifiedJobMetrics:
        job_by_name = [job for job in jobs if job.name == job_identifier.name]
        return IdentifiedJobMetrics(
            job_identifier=job_identifier,
            metrics=self._compute_job_metrics(job_by_name),
        )

    def _compute_job_metrics(self, jobs: list[JobDetails]) -> JobMetrics:
        total_jobs_number = len(jobs)
        successful_jobs_number = self._get_number_of_jobs_by_state(
            jobs=jobs, job_state=JobState.SUCCESS
        )
        if total_jobs_number == 0:
            return JobMetrics(successes=0, failures=0)
        return JobMetrics(
            successes=successful_jobs_number,
            failures=total_jobs_number - successful_jobs_number,
        )

    def _get_top_n_jobs(
        self,
        jobs: list[JobDetails],
        n: int,
        comparison_func: Callable,
    ) -> list[IdentifiedJobMetrics]:
        distinct_jobs = {JobIdentifier.create_from_job_details(job) for job in jobs}
        res = [
            self._get_job_metrics(job_identifier, jobs)
            for job_identifier in distinct_jobs
        ]
        res = sorted(res, key=comparison_func, reverse=True)
        res = res[0 : min(len(res), n)]
        res.reverse()
        return res

    def _get_top_n_failed_jobs(
        self,
        jobs: list[JobDetails],
        n: int,
    ) -> list[IdentifiedJobMetrics]:
        top_failed_jobs = self._get_top_n_jobs(
            jobs=jobs,
            n=n,
            comparison_func=lambda identified_job_metrics: (
                identified_job_metrics.metrics.failure_rate,
                identified_job_metrics.metrics.failures,
                identified_job_metrics.job_identifier.name,
            ),
        )
        return [
            identified_job
            for identified_job in top_failed_jobs
            if identified_job.metrics.failures > 0
        ]

    @staticmethod
    def _is_rehearsal(job: JobDetails) -> bool:
        return (
            "rehearse" in job.name
            and job.type == "presubmit"
            and job.refs.repo == "release"
            and job.refs.org == "openshift"
        )

    @staticmethod
    def _is_assisted_repository(job: JobDetails) -> bool:
        return (
            job.refs.repo
            in [
                "assisted-service",
                "assisted-installer",
                "assisted-installer-agent",
                "assisted-image-service",
                "assisted-test-infra",
                "cluster-api-provider-agent",
            ]
            and job.refs.org == "openshift"
        )

    @staticmethod
    def _is_e2e_or_subsystem_class(job: JobDetails) -> bool:
        return "e2e" in job.name or "subsystem" in job.name

    def get_report(self, from_date: datetime, to_date: datetime) -> Report:
        jobs = self._querier.query_jobs(from_date=from_date, to_date=to_date)
        logger.debug("%d jobs queried from elasticsearch", len(jobs))
        step_events = self._querier.query_packet_setup_step_events(
            from_date=from_date, to_date=to_date
        )
        logger.debug("%d step events queried from elasticsearch", len(step_events))
        rehearsal_jobs = [job for job in jobs if self._is_rehearsal(job=job)]
        assisted_components_jobs = [
            job for job in jobs if self._is_assisted_repository(job)
        ]
        subsystem_and_e2e_jobs = [
            job
            for job in assisted_components_jobs
            if self._is_e2e_or_subsystem_class(job)
        ]
        periodic_subsystem_and_e2e_jobs = [
            job for job in subsystem_and_e2e_jobs if job.type == JobType.PERIODIC.value
        ]
        presubmit_subsystem_and_e2e_jobs = [
            job for job in subsystem_and_e2e_jobs if job.type == JobType.PRESUBMIT.value
        ]
        postsubmit_jobs = [
            job
            for job in assisted_components_jobs
            if job.type == JobType.POSTSUBMIT.value
        ]

        return Report(
            from_date=from_date,
            to_date=to_date,
            number_of_e2e_or_subsystem_periodic_jobs=len(
                periodic_subsystem_and_e2e_jobs
            ),
            number_of_successful_e2e_or_subsystem_periodic_jobs=self._get_number_of_jobs_by_state(
                jobs=periodic_subsystem_and_e2e_jobs, job_state=JobState.SUCCESS
            ),
            number_of_failing_e2e_or_subsystem_periodic_jobs=self._get_number_of_jobs_by_state(
                jobs=periodic_subsystem_and_e2e_jobs, job_state=JobState.FAILURE
            ),
            success_rate_for_e2e_or_subsystem_periodic_jobs=self._compute_job_metrics(
                jobs=periodic_subsystem_and_e2e_jobs
            ).success_rate,
            top_10_failing_e2e_or_subsystem_periodic_jobs=self._get_top_n_failed_jobs(
                jobs=periodic_subsystem_and_e2e_jobs,
                n=10,
            ),
            number_of_e2e_or_subsystem_presubmit_jobs=len(
                presubmit_subsystem_and_e2e_jobs
            ),
            number_of_successful_e2e_or_subsystem_presubmit_jobs=self._get_number_of_jobs_by_state(
                jobs=presubmit_subsystem_and_e2e_jobs, job_state=JobState.SUCCESS
            ),
            number_of_failing_e2e_or_subsystem_presubmit_jobs=self._get_number_of_jobs_by_state(
                jobs=presubmit_subsystem_and_e2e_jobs, job_state=JobState.FAILURE
            ),
            number_of_rehearsal_jobs=len(rehearsal_jobs),
            success_rate_for_e2e_or_subsystem_presubmit_jobs=self._compute_job_metrics(
                jobs=presubmit_subsystem_and_e2e_jobs
            ).success_rate,
            top_10_failing_e2e_or_subsystem_presubmit_jobs=self._get_top_n_failed_jobs(
                jobs=presubmit_subsystem_and_e2e_jobs,
                n=10,
            ),
            top_5_most_triggered_e2e_or_subsystem_jobs=self._get_top_n_jobs(
                jobs=presubmit_subsystem_and_e2e_jobs,
                n=5,
                comparison_func=lambda identified_job_metrics: (
                    identified_job_metrics.metrics.total,
                    identified_job_metrics.job_identifier.name,
                ),
            ),
            number_of_postsubmit_jobs=len(postsubmit_jobs),
            number_of_successful_postsubmit_jobs=self._get_number_of_jobs_by_state(
                jobs=postsubmit_jobs, job_state=JobState.SUCCESS
            ),
            number_of_failing_postsubmit_jobs=self._get_number_of_jobs_by_state(
                jobs=postsubmit_jobs, job_state=JobState.FAILURE
            ),
            success_rate_for_postsubmit_jobs=self._compute_job_metrics(
                jobs=postsubmit_jobs
            ).success_rate,
            top_10_failing_postsubmit_jobs=self._get_top_n_failed_jobs(
                jobs=postsubmit_jobs,
                n=10,
            ),
            number_of_successful_machine_leases=len(
                [
                    step_event
                    for step_event in step_events
                    if step_event.step.state == StepState.SUCCESS.value
                ]
            ),
            number_of_unsuccessful_machine_leases=len(
                [
                    step_event
                    for step_event in step_events
                    if step_event.step.state == StepState.FAILURE.value
                ]
            ),
            total_number_of_machine_leased=len(step_events),
        )
