import logging
from datetime import datetime
from typing import Callable

from projects.jobsautoreport.models import (
    IdentifiedJobMetrics,
    JobIdentifier,
    JobMetrics,
    JobState,
    JobType,
    Report,
    StepState,
)
from projects.jobsautoreport.query import Querier
from projects.prowjobsscraper.event import JobDetails

logger = logging.getLogger(__name__)


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
