from datetime import datetime, timedelta
from importlib import resources
from typing import Any, Iterator, Optional

from opensearchpy import OpenSearch, helpers
from pydantic import BaseModel

from prowjobsscraper.prowjob import CIResourceMetadata, ProwJob
from prowjobsscraper.step import JobStep
from prowjobsscraper.utils import generate_hash_from_strings


class JobRefs(BaseModel):
    base_ref: Optional[str]
    org: Optional[str]
    pull: Optional[str]
    repo: Optional[str]

    @classmethod
    def create_from_prow_job(cls, job: ProwJob) -> "JobRefs":
        return cls(
            base_ref=job.metadata.labels.refsBaseRef,
            org=job.metadata.labels.refsOrg,
            pull=job.metadata.labels.refsPull,
            repo=job.metadata.labels.refsRepo,
        )


class JobDetails(BaseModel):
    build_id: Optional[str]
    cloud_cluster_profile: Optional[str]
    cloud: Optional[str]
    context: Optional[str]
    duration: int
    ci_resource_metadata: Optional[CIResourceMetadata]
    name: str
    refs: JobRefs
    start_time: Optional[datetime]
    state: Optional[str]
    type: str
    url: Optional[str]
    variant: Optional[str]


class JobEvent(BaseModel):
    job: JobDetails

    @classmethod
    def create_from_prow_job(cls, job: ProwJob) -> "JobEvent":
        job_duration = timedelta(seconds=0)
        if job.status.completionTime and job.status.startTime:
            job_duration = job.status.completionTime - job.status.startTime

        return cls(
            job=JobDetails(
                build_id=job.status.build_id,
                cloud_cluster_profile=job.metadata.labels.cloudClusterProfile,
                cloud=job.metadata.labels.cloud,
                context=job.context,
                duration=job_duration.seconds,
                ci_resource_metadata=job.cirMetadata,
                name=job.spec.job,
                refs=JobRefs.create_from_prow_job(job),
                start_time=job.status.startTime,
                state=job.status.state,
                type=job.spec.type,
                url=job.status.url,
                variant=job.metadata.labels.variant,
            )
        )


class StepDetails(BaseModel):
    details: Optional[str]
    duration: int
    name: str
    state: str


class StepEvent(BaseModel):
    job: JobDetails
    step: StepDetails

    @classmethod
    def create_from_job_step(cls, step: JobStep) -> "StepEvent":
        return cls(
            job=JobEvent.create_from_prow_job(step.job).job,
            step=StepDetails(
                details=step.details,
                duration=step.duration.seconds,
                name=step.name,
                state=step.state,
            ),
        )


class EventStoreElastic:
    def __init__(self, client, job_index_basename, step_index_basename):
        self._jobs_index = _EsIndex(client, job_index_basename)
        self._steps_index = _EsIndex(client, step_index_basename)

    def index_job_steps(self, steps: list[JobStep]):
        step_events = (
            (
                StepEvent.create_from_job_step(s).dict(),
                generate_hash_from_strings(s.job.status.build_id, s.name),
            )
            for s in steps
        )
        self._steps_index.index(step_events)

    def index_prow_jobs(self, jobs: list[ProwJob]):
        job_events = (
            (JobEvent.create_from_prow_job(j).dict(), j.status.build_id) for j in jobs
        )
        self._jobs_index.index(job_events)

    def scan_build_ids(self) -> set[str]:
        results = self._jobs_index.scan({"_source": ["job.build_id"]})
        return {r["_source"]["job"]["build_id"] for r in results}


class _EsIndex:
    def __init__(self, client: OpenSearch, index_prefix: str):
        self._client = client

        # Let's create one index per week
        now = datetime.now()
        self._index_name = self._format_index_name(index_prefix, now)

        a_week_ago = now - timedelta(weeks=1)
        self._previous_index_name = self._format_index_name(index_prefix, a_week_ago)

        # apply the index template
        index_schema = (
            resources.files(__package__)
            .joinpath(f"indices/{index_prefix}_schema.json")
            .read_bytes()
        )
        if not self._client.indices.exists(index=self._index_name):
            self._client.indices.create(index=self._index_name, body=index_schema)

    @staticmethod
    def _format_index_name(prefix: str, date: datetime) -> str:
        iso_calendar = date.isocalendar()
        # keep the same format as strftime("%W") for week number
        return f"{prefix}-{iso_calendar.year}.{iso_calendar.week:02d}"

    def _gen_documents(
        self, data: Iterator[tuple[dict[str, Any], str]]
    ) -> Iterator[dict[str, Any]]:
        for d, id in data:
            yield {
                "_index": self._index_name,
                "_op_type": "update",
                "_id": id,
                "doc_as_upsert": True,
                "doc": d,
            }

    def index(self, data: Iterator[tuple[dict[str, Any], str]]) -> None:
        helpers.bulk(self._client, self._gen_documents(data))

        self._client.indices.refresh(index=self._index_name)

    def scan(self, query: str) -> Iterator[Any]:
        return helpers.scan(
            self._client,
            index=f"{self._index_name},{self._previous_index_name}",
            ignore_unavailable=True,
            query=query,
        )
