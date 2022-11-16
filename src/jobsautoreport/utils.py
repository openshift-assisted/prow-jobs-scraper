from prowjobsscraper.event import JobDetails


def parse_jobs(data: dict) -> list[JobDetails]:
    jobs_list = [parse_job(job["_source"]["job"]) for job in data["hits"]["hits"]]
    return jobs_list


def parse_job(data: dict) -> JobDetails:
    return JobDetails.parse_obj(data)
