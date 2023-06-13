import logging
from datetime import datetime
from typing import Any, Callable, Optional, Union

import numpy as np
from pydantic import BaseModel

from jobsautoreport.models import (
    JobMetrics,
    JobState,
    JobType,
    JobTypeMetrics,
    MachineMetrics,
    StepState,
)
from jobsautoreport.query import Querier
from prowjobsscraper.equinix_usages import EquinixUsageEvent
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
    total_equinix_machines_cost: float
    cost_by_machine_type: MachineMetrics
    cost_by_job_type: JobTypeMetrics
    top_5_most_expensive_jobs: list[IdentifiedJobMetrics]
    flaky_jobs: list[IdentifiedJobMetrics]


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
        usages: list[EquinixUsageEvent],
    ) -> IdentifiedJobMetrics:
        job_by_name = [job for job in jobs if job.name == job_identifier.name]
        return IdentifiedJobMetrics(
            job_identifier=job_identifier,
            metrics=self._compute_job_metrics(job_by_name, usages),
        )

    def _compute_job_metrics(
        self, jobs: list[JobDetails], usages: list[EquinixUsageEvent]
    ) -> JobMetrics:
        total_jobs_number = len(jobs)
        if total_jobs_number == 0:
            return JobMetrics(successes=0, failures=0, cost=0, flakiness=None)

        successful_jobs_number = self._get_number_of_jobs_by_state(
            jobs=jobs, job_state=JobState.SUCCESS
        )
        total_cost = sum(
            [
                self._compute_job_cost(usages, job.build_id)
                for job in jobs
                if job.build_id is not None
            ]
        )
        flakiness = self._compute_flakiness(jobs)

        return JobMetrics(
            successes=successful_jobs_number,
            failures=total_jobs_number - successful_jobs_number,
            cost=total_cost,
            flakiness=flakiness,
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

    @staticmethod
    def _compute_job_cost(usages: list[EquinixUsageEvent], build_id: str) -> float:
        return sum(
            [usage.usage.total for usage in usages if usage.job.build_id == build_id]
        )

    def _get_top_n_jobs(
        self,
        jobs: list[JobDetails],
        n: int,
        comparison_func: Callable,
        usages: list[EquinixUsageEvent],
    ) -> list[IdentifiedJobMetrics]:
        distinct_jobs = {JobIdentifier.create_from_job_details(job) for job in jobs}
        res = [
            self._get_job_metrics(job_identifier, jobs, usages)
            for job_identifier in distinct_jobs
        ]
        res = sorted(res, key=comparison_func, reverse=True)
        res = res[0 : min(len(res), n)]
        res.reverse()
        return res

    def _get_top_n_failed_jobs(
        self, jobs: list[JobDetails], n: int, usages: list[EquinixUsageEvent]
    ) -> list[IdentifiedJobMetrics]:
        top_failed_jobs = self._get_top_n_jobs(
            jobs=jobs,
            n=n,
            comparison_func=lambda identified_job_metrics: (
                identified_job_metrics.metrics.failure_rate,
                identified_job_metrics.metrics.failures,
                identified_job_metrics.job_identifier.name,
            ),
            usages=usages,
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

    @classmethod
    def _get_machine_metrics(cls, usages: list[EquinixUsageEvent]) -> MachineMetrics:
        machine_types = {usage.usage.plan for usage in usages}
        return MachineMetrics(
            metrics={
                machine_type: cls._count_cost_by_machine_type(usages, machine_type)
                for machine_type in machine_types
            }
        )

    @staticmethod
    def _count_cost_by_machine_type(
        usages: list[EquinixUsageEvent], machine_type: str
    ) -> float:
        return sum(
            [usage.usage.total for usage in usages if usage.usage.plan == machine_type]
        )

    @classmethod
    def _get_job_type_metrics(
        cls, usages: list[EquinixUsageEvent], jobs: list[JobDetails]
    ) -> JobTypeMetrics:
        job_types = {job.type for job in jobs}
        return JobTypeMetrics(
            metrics={
                job_type: cls._count_cost_by_job_type(usages, jobs, job_type)
                for job_type in job_types
            }
        )

    @staticmethod
    def _count_cost_by_job_type(
        usages: list[EquinixUsageEvent], jobs: list[JobDetails], job_type: str
    ) -> float:
        jobs_build_id_to_type = {job.build_id: job.type for job in jobs}
        return sum(
            [
                usage.usage.total
                for usage in usages
                if jobs_build_id_to_type.get(usage.job.build_id) == job_type
            ]
        )

    def _get_top_n_most_expensive_jobs(
        self, jobs: list[JobDetails], usages: list[EquinixUsageEvent], n: int
    ) -> list[IdentifiedJobMetrics]:
        most_expensive_jobs = self._get_top_n_jobs(
            jobs=jobs,
            n=n,
            comparison_func=lambda identified_job_metrics: (
                identified_job_metrics.metrics.cost,
                identified_job_metrics.job_identifier.name,
            ),
            usages=usages,
        )
        return [
            identified_job
            for identified_job in most_expensive_jobs
            if identified_job.metrics.cost > 0
        ]

    def _get_flaky_jobs(
        self, jobs: list[JobDetails], usages: list[EquinixUsageEvent]
    ) -> list[IdentifiedJobMetrics]:
        distinct_jobs = {JobIdentifier.create_from_job_details(job) for job in jobs}
        flaky_jobs: list[IdentifiedJobMetrics] = []
        for job_identifier in distinct_jobs:
            jobs_by_name = [job for job in jobs if job_identifier.name == job.name]
            job_metrics: JobMetrics = self._compute_job_metrics(
                jobs=jobs_by_name, usages=usages
            )
            if job_metrics.is_flaky():
                flaky_jobs.append(
                    IdentifiedJobMetrics(
                        job_identifier=job_identifier, metrics=job_metrics
                    )
                )

        sorted_flaky_jobs = sorted(flaky_jobs, key=lambda job_identifier: job_identifier.metrics.flakiness, reverse=True)  # type: ignore
        flaky_jobs = flaky_jobs[0 : min(len(sorted_flaky_jobs), 10)]
        flaky_jobs.reverse()

        return sorted_flaky_jobs

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

        usages = self._querier.query_usage_events(from_date=from_date, to_date=to_date)

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
                jobs=periodic_subsystem_and_e2e_jobs, usages=usages
            ).success_rate,
            top_10_failing_e2e_or_subsystem_periodic_jobs=self._get_top_n_failed_jobs(
                jobs=periodic_subsystem_and_e2e_jobs, n=10, usages=usages
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
                jobs=presubmit_subsystem_and_e2e_jobs, usages=usages
            ).success_rate,
            top_10_failing_e2e_or_subsystem_presubmit_jobs=self._get_top_n_failed_jobs(
                jobs=presubmit_subsystem_and_e2e_jobs, n=10, usages=usages
            ),
            top_5_most_triggered_e2e_or_subsystem_jobs=self._get_top_n_jobs(
                jobs=presubmit_subsystem_and_e2e_jobs,
                n=5,
                comparison_func=lambda identified_job_metrics: (
                    identified_job_metrics.metrics.total,
                    identified_job_metrics.job_identifier.name,
                ),
                usages=usages,
            ),
            number_of_postsubmit_jobs=len(postsubmit_jobs),
            number_of_successful_postsubmit_jobs=self._get_number_of_jobs_by_state(
                jobs=postsubmit_jobs, job_state=JobState.SUCCESS
            ),
            number_of_failing_postsubmit_jobs=self._get_number_of_jobs_by_state(
                jobs=postsubmit_jobs, job_state=JobState.FAILURE
            ),
            success_rate_for_postsubmit_jobs=self._compute_job_metrics(
                jobs=postsubmit_jobs, usages=usages
            ).success_rate,
            top_10_failing_postsubmit_jobs=self._get_top_n_failed_jobs(
                jobs=postsubmit_jobs, n=10, usages=usages
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
            total_equinix_machines_cost=sum(usage.usage.total for usage in usages),
            cost_by_machine_type=self._get_machine_metrics(usages),
            cost_by_job_type=self._get_job_type_metrics(
                usages, assisted_components_jobs
            ),
            top_5_most_expensive_jobs=self._get_top_n_most_expensive_jobs(
                jobs=assisted_components_jobs, usages=usages, n=5
            ),
            flaky_jobs=self._get_flaky_jobs(
                jobs=assisted_components_jobs, usages=usages
            ),
        )
