from typing import Any

from prowjobsscraper.event import JobDetails


def parse_jobs(data: list[dict[Any, Any]]) -> list[JobDetails]:
    jobs_list = [parse_job(job["_source"]["job"]) for job in data]
    return jobs_list


def parse_job(data: dict) -> JobDetails:
    return JobDetails.parse_obj(data)
