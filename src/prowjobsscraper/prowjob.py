from __future__ import annotations

import logging
from datetime import datetime
from typing import Final, Optional

import requests
from pydantic import BaseModel, Field, HttpUrl

logger = logging.getLogger(__name__)

# Map job type with the prefix string in job name
_TYPE_PREFIX: Final[dict[str, str]] = {
    "periodic": "periodic-ci",
    "presubmit": "pull-ci",
    "batch": "pull-ci",
    "postsubmit": "branch-ci",
}


_JOB_REHEARSE_PREFIX: Final[str] = "rehearse-"

# Base prefix for a job name
# e.g.: {branch-ci}-{openshift}-{assisted-service}-{master}-
_JOB_PREFIX_TEMPLATE: Final[str] = "{type}-{org}-{repo}-{branch}-"


class CIResourceMetadata(BaseModel):
    """
    CIResourceMetadata represents the metadata of a CI resource.
    """

    ip: Optional[str] = None
    name: Optional[str] = None
    pool: Optional[str] = None
    provider: Optional[str] = None
    providerInfo: Optional[str] = None
    type: Optional[str] = None
    region: Optional[str] = None
    hostname: Optional[str] = None
    os: Optional[str] = None

    @classmethod
    def create_from_cir_metadata(
        cls, cir_metadata: Optional[CIResourceMetadata]
    ) -> Optional["CIResourceMetadata"]:
        if cir_metadata:
            return cls(
                ip=cir_metadata.ip,
                name=cir_metadata.name,
                pool=cir_metadata.pool,
                provider=cir_metadata.provider,
                providerInfo=cir_metadata.providerInfo,
                type=cir_metadata.type,
                region=cir_metadata.region,
                hostname=cir_metadata.hostname,
                os=cir_metadata.os,
            )

        return None


class ProwJobMetadataLabels(BaseModel):
    cloud: Optional[str] = Field(None, alias="ci-operator.openshift.io/cloud")
    cloudClusterProfile: Optional[str] = Field(
        None, alias="ci-operator.openshift.io/cloud-cluster-profile"
    )
    refsBaseRef: Optional[str] = Field(None, alias="prow.k8s.io/refs.base_ref")
    refsOrg: Optional[str] = Field(None, alias="prow.k8s.io/refs.org")
    refsPull: Optional[str] = Field(None, alias="prow.k8s.io/refs.pull")
    refsRepo: Optional[str] = Field(None, alias="prow.k8s.io/refs.repo")
    variant: Optional[str] = Field(None, alias="ci-operator.openshift.io/variant")


class ProwJobMetadata(BaseModel):
    labels: ProwJobMetadataLabels


class ProwJobRef(BaseModel):
    org: str
    repo: str
    base_ref: str


class ProwJobSpec(BaseModel):
    job: str
    type: str
    hidden: Optional[bool]
    extra_refs: Optional[list[ProwJobRef]]


class ProwJobStatus(BaseModel):
    state: Optional[str] = None
    url: Optional[HttpUrl] = None
    startTime: Optional[datetime] = None
    pendingTime: Optional[datetime] = None
    completionTime: Optional[datetime] = None
    build_id: Optional[str] = None
    description: Optional[str] = None


class ProwJob(BaseModel):
    cirMetadata: Optional[CIResourceMetadata] = None
    metadata: ProwJobMetadata
    spec: ProwJobSpec
    status: ProwJobStatus

    @property
    def context(self) -> str:
        if self.spec.job.startswith(_JOB_REHEARSE_PREFIX):
            job_prefix = self._get_job_rehearse_prefix()
        else:
            job_prefix = self._get_job_prefix()

        context = self.spec.job.removeprefix(job_prefix)
        logger.debug(
            "job=%s job_prefix=%s context=%s : %s",
            self.spec.job,
            job_prefix,
            context,
            self,
        )
        return context

    def _get_job_prefix(self) -> str:
        if not (
            self.metadata.labels.refsOrg
            and self.metadata.labels.refsRepo
            and self.metadata.labels.refsBaseRef
        ):
            logger.warning("Job name cannot be sanitized %s", self)
            return self.spec.job

        job_prefix = _JOB_PREFIX_TEMPLATE.format(
            type=_TYPE_PREFIX[self.spec.type],
            org=self.metadata.labels.refsOrg,
            repo=self.metadata.labels.refsRepo,
            branch=self.metadata.labels.refsBaseRef,
        )
        if self.metadata.labels.variant:
            job_prefix = f"{job_prefix}{self.metadata.labels.variant}-"

        return job_prefix

    def _get_job_rehearse_prefix(self) -> str:
        if not self.spec.extra_refs or len(self.spec.extra_refs) != 1:
            logger.warning(
                "Invalid extra_refs to determine rehearse job context %s", self
            )
            return self.spec.job

        if not self.metadata.labels.refsPull:
            logger.warning(
                "refsPull is required to determine rehearse job context %s", self
            )
            return self.spec.job

        job_prefix = f"{_JOB_REHEARSE_PREFIX}{self.metadata.labels.refsPull}-"

        ref = self.spec.extra_refs[0]
        job_prefix = job_prefix + _JOB_PREFIX_TEMPLATE.format(
            type=_TYPE_PREFIX[self.spec.type],
            org=ref.org,
            repo=ref.repo,
            branch=ref.base_ref,
        )
        if self.metadata.labels.variant:
            job_prefix = f"{job_prefix}{self.metadata.labels.variant}-"

        return job_prefix


class ProwJobs(BaseModel):
    """
    ProwJobs represents the data structure returned by Prow's API
    (e.g.: https://prow.ci.openshift.org/prowjobs.js?omit=annotations,decoration_config,pod_spec)
    """

    items: list[ProwJob]

    @classmethod
    def create_from_url(cls, url: str) -> "ProwJobs":
        r = requests.get(url)
        return cls.create_from_string(r.text)

    @classmethod
    def create_from_string(cls, data: str) -> "ProwJobs":
        jobs = cls.parse_raw(data)
        return jobs
