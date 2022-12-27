from datetime import datetime
from typing import Any, Callable

from pydantic import BaseModel

from jobsautoreport.models import JobState, JobType, StepState
from jobsautoreport.query import Querier
from prowjobsscraper.event import JobDetails


class JobStatesCount(BaseModel):

    successes: int
    failures: int
    success_rate: float

    def __str__(self) -> str:
        return (
            f"successes: {self.successes}\n"
            f"failures: {self.failures}\n"
            f"success_rate: {self.success_rate}"
        )


class Report(BaseModel):

    number_of_e2e_or_subsystem_periodic_jobs: int
    number_of_successful_e2e_or_subsystem_periodic_jobs: int
    number_of_failing_e2e_or_subsystem_periodic_jobs: int
    success_rate_for_e2e_or_subsystem_periodic_jobs: float
    top_10_failing_e2e_or_subsystem_periodic_jobs: list[tuple[str, JobStatesCount]]
    number_of_e2e_or_subsystem_presubmit_jobs: int
    number_of_successful_e2e_or_subsystem_presubmit_jobs: int
    number_of_failing_e2e_or_subsystem_presubmit_jobs: int
    number_of_rehearsal_jobs: int
    success_rate_for_e2e_or_subsystem_presubmit_jobs: float
    top_10_failing_e2e_or_subsystem_presubmit_jobs: list[tuple[str, JobStatesCount]]
    top_5_most_triggered_e2e_or_subsystem_jobs: list[tuple[str, int]]
    number_of_successful_machine_leases: int
    number_of_unsuccessful_machine_leases: int
    total_number_of_machine_leased: int

    def __str__(self) -> str:
        return (
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

    def _get_job_states_count(
        self, job_name: str, jobs: list[JobDetails]
    ) -> JobStatesCount:
        job_by_name = [job for job in jobs if job.name == job_name]
        return self._get_states_count(job_by_name)

    @staticmethod
    def _get_number_of_jobs_by_state(
        jobs: list[JobDetails], job_state: JobState
    ) -> int:
        return len([job for job in jobs if job.state == job_state.value])

    def _get_states_count(self, jobs: list[JobDetails]) -> JobStatesCount:
        total_jobs_number = len(jobs)
        successful_jobs_number = self._get_number_of_jobs_by_state(
            jobs=jobs, job_state=JobState.SUCCESS
        )
        return (
            JobStatesCount(successes=0, failures=0, success_rate=0.0)
            if total_jobs_number == 0
            else JobStatesCount(
                successes=successful_jobs_number,
                failures=total_jobs_number - successful_jobs_number,
                success_rate=float(
                    round((successful_jobs_number / total_jobs_number) * 100, 2)
                ),
            )
        )

    @staticmethod
    def _get_top_n_jobs(
        jobs: list[JobDetails],
        computation_func: Callable[[str, list[JobDetails]], Any],
        n: int,
        comparison_func: Callable,
        is_reverse: bool = False,
    ) -> list[tuple[str, Any]]:
        distinct_jobs = {job.name for job in jobs}
        res = [
            (job_name, computation_func(job_name, jobs)) for job_name in distinct_jobs
        ]
        res = sorted(res, key=comparison_func, reverse=is_reverse)
        return res[0 : min(len(res), n)]

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
        step_events = self._querier.query_packet_setup_step_events(
            from_date=from_date, to_date=to_date
        )
        rehearsal_jobs = [job for job in jobs if self._is_rehearsal(job=job)]
        subsystem_and_e2e_jobs = [
            job
            for job in jobs
            if self._is_assisted_repository(job)
            and self._is_e2e_or_subsystem_class(job)
        ]
        periodic_subsystem_and_e2e_jobs = [
            job for job in subsystem_and_e2e_jobs if job.type == JobType.PERIODIC.value
        ]
        presubmit_subsystem_and_e2e_jobs = [
            job for job in subsystem_and_e2e_jobs if job.type == JobType.PRESUBMIT.value
        ]

        return Report(
            number_of_e2e_or_subsystem_periodic_jobs=len(
                periodic_subsystem_and_e2e_jobs
            ),
            number_of_successful_e2e_or_subsystem_periodic_jobs=self._get_number_of_jobs_by_state(
                jobs=periodic_subsystem_and_e2e_jobs, job_state=JobState.SUCCESS
            ),
            number_of_failing_e2e_or_subsystem_periodic_jobs=self._get_number_of_jobs_by_state(
                jobs=periodic_subsystem_and_e2e_jobs, job_state=JobState.FAILURE
            ),
            success_rate_for_e2e_or_subsystem_periodic_jobs=self._get_states_count(
                jobs=periodic_subsystem_and_e2e_jobs
            ).success_rate,
            top_10_failing_e2e_or_subsystem_periodic_jobs=self._get_top_n_jobs(
                jobs=periodic_subsystem_and_e2e_jobs,
                computation_func=self._get_job_states_count,
                n=10,
                comparison_func=lambda job: (job[1].success_rate, job[0]),
                is_reverse=True,
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
            success_rate_for_e2e_or_subsystem_presubmit_jobs=self._get_states_count(
                jobs=presubmit_subsystem_and_e2e_jobs
            ).success_rate,
            top_10_failing_e2e_or_subsystem_presubmit_jobs=self._get_top_n_jobs(
                jobs=presubmit_subsystem_and_e2e_jobs,
                computation_func=self._get_job_states_count,
                n=10,
                comparison_func=lambda job: (job[1].success_rate, job[0]),
                is_reverse=True,
            ),
            top_5_most_triggered_e2e_or_subsystem_jobs=self._get_top_n_jobs(
                jobs=subsystem_and_e2e_jobs,
                computation_func=self._get_job_triggers_count,
                n=5,
                comparison_func=lambda job: (job[1], job[0]),
                is_reverse=False,
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
