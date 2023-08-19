import logging
from datetime import datetime
from typing import Any, Callable, Optional, Union

import numpy as np
from pydantic import BaseModel

from jobsautoreport.models import JobMetrics, JobState, JobType, StepState
from jobsautoreport.query import Querier
from prowjobsscraper.event import JobDetails

logger = logging.getLogger(__name__)


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


class Report(BaseModel):
    from_date: datetime
    to_date: datetime
    number_of_e2e_or_subsystem_periodic_jobs: int
    number_of_successful_e2e_or_subsystem_periodic_jobs: int
    number_of_failing_e2e_or_subsystem_periodic_jobs: int
    success_rate_for_e2e_or_subsystem_periodic_jobs: Optional[float]
    top_10_failing_e2e_or_subsystem_periodic_jobs: list[IdentifiedJobMetrics]
    number_of_e2e_or_subsystem_presubmit_jobs: int
    number_of_successful_e2e_or_subsystem_presubmit_jobs: int
    number_of_failing_e2e_or_subsystem_presubmit_jobs: int
    number_of_rehearsal_jobs: int
    success_rate_for_e2e_or_subsystem_presubmit_jobs: Optional[float]
    top_10_failing_e2e_or_subsystem_presubmit_jobs: list[IdentifiedJobMetrics]
    top_5_most_triggered_e2e_or_subsystem_jobs: list[IdentifiedJobMetrics]
    number_of_postsubmit_jobs: int
    number_of_successful_postsubmit_jobs: int
    number_of_failing_postsubmit_jobs: int
    success_rate_for_postsubmit_jobs: Optional[float]
    top_10_failing_postsubmit_jobs: list[IdentifiedJobMetrics]
    number_of_successful_machine_leases: int
    number_of_unsuccessful_machine_leases: int
    total_number_of_machine_leased: int


class Reporter:
    """Reporter computes metrics from the data Querier retrieves, and generates report"""

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
        self,
        job_identifier: JobIdentifier,
        jobs: list[JobDetails],
    ) -> IdentifiedJobMetrics:
        job_by_name = [job for job in jobs if job.name == job_identifier.name]
        return IdentifiedJobMetrics(
            job_identifier=job_identifier,
            metrics=self._compute_job_metrics(job_by_name),
        )

    def _compute_job_metrics(self, jobs: list[JobDetails]) -> JobMetrics:
        total_jobs_number = len(jobs)
        if total_jobs_number == 0:
            return JobMetrics(successes=0, failures=0)

        successful_jobs_number = self._get_number_of_jobs_by_state(
            jobs=jobs, job_state=JobState.SUCCESS
        )

        return JobMetrics(
            successes=successful_jobs_number,
            failures=total_jobs_number - successful_jobs_number,
        )

    @staticmethod
    def _compute_flakiness(jobs: list[JobDetails]) -> Optional[float]:
        filtered_jobs = [job for job in jobs if job.start_time is not None]
        jobs_by_start_time = sorted(filtered_jobs, key=lambda job: job.start_time)  # type: ignore
        jobs_states_by_start_time = [
            job.state for job in jobs_by_start_time if job.state is not None
        ]
        numeral_jobs_states_by_start_time = list(
            map(lambda state: 1 if state == "success" else 0, jobs_states_by_start_time)
        )
        if len(jobs_states_by_start_time) == 0:
            return None

        elif len(jobs_states_by_start_time) == 1:
            return 0

        # Flakiness is defined as the weighted average of adjacent absolute differences between job executions (weight is increasing)
        # that way recent flakiness counts more than old flakiness
        states_array = np.array(numeral_jobs_states_by_start_time)
        diffs = np.diff(states_array)
        absolute_diffs = np.abs(diffs)
        # weights sum up to 1
        weights = np.linspace(0.1, 1, len(absolute_diffs)) / sum(
            np.linspace(0.1, 1, len(absolute_diffs))
        )
        weighted_average_diffs = np.average(absolute_diffs, weights=weights)

        return weighted_average_diffs

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
                jobs=periodic_subsystem_and_e2e_jobs, n=10
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
                jobs=presubmit_subsystem_and_e2e_jobs, n=10
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
                jobs=postsubmit_jobs, n=10
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
