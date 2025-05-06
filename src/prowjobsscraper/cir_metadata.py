import logging
from typing import Final, Optional

from google.cloud import exceptions, storage  # type: ignore

from providers.provider import get_provider_by_id
from prowjobsscraper import utils
from prowjobsscraper.prowjob import (
    CIResourceMetadata,
    ProwJob,
    ProwJobs,
)

logger = logging.getLogger(__name__)


class CIResourceMetadataExtractor:

    _CIR_METADATA_PATH_TEMPLATE: Final[str] = (
        "{}/artifacts/{}/ofcir-gather/artifacts/cir.json"
    )
    _PACKET: Final[str] = "packet"

    def __init__(self, client: storage.Client, gcs_bucket_name: str):
        self._client = client
        self._gcs_bucket_name = gcs_bucket_name

    def hydrate(self, jobs: ProwJobs) -> None:
        for job in jobs.items:
            self._set_cir_metadata(job)

    def _get_metadata(self, path: str) -> Optional[str]:
        try:
            raw_metadata = utils.download_from_gcs_as_string(
                self._client, self._gcs_bucket_name, path
            )
            logger.debug("Found metadata: %s", path)
            return raw_metadata

        except exceptions.ClientError as e:
            logger.debug("Metadata are missing from %s: %s", path, e)
            return None

    def _get_cir_metadata(
        self, base_path: str, job: ProwJob
    ) -> Optional[CIResourceMetadata]:
        metadata_path = self._CIR_METADATA_PATH_TEMPLATE.format(base_path, job.context)
        raw_metadata = self._get_metadata(metadata_path)

        if not raw_metadata:
            logger.info("No metadata found for job %s", job)
            return None

        try:
            cir_metadata = CIResourceMetadata.parse_raw(raw_metadata)
            logger.debug("Decoded successfully CIR metadata in: %s", metadata_path)
            return cir_metadata

        except Exception as e:
            logger.warning(
                f"Failed to decode ci resource metadata for job {job.spec.job}: {e}"
            )
            return None

    def _should_job_have_metadata(self, job: ProwJob) -> bool:
        return (
            job.metadata.labels.cloudClusterProfile is not None
            and self._PACKET in job.metadata.labels.cloudClusterProfile
        )

    def _set_cir_metadata(self, job: ProwJob) -> None:
        if not self._should_job_have_metadata(job=job):
            logger.debug(
                "Job %s is not a packet job, skipping CIR metadata collection", job
            )
            return

        base_path = utils.get_gcs_base_path_from_job_url(job.status.url)
        if (cir_metadata := self._get_cir_metadata(base_path, job)) is None:
            logger.debug("No CIR metadata found for job %s", job)
            return

        if not cir_metadata.provider:
            logger.debug("No provider found in CIR metadata for job %s", job)
            return

        if cir_metadata.provider == "ibmcloud":
            cir_metadata.provider = "ibm-classic"

        if (provider := get_provider_by_id(id=cir_metadata.provider)) is None:
            logger.debug(
                "provider ID %s in job %s doesn't match any supported provider",
                cir_metadata.provider,
                job,
            )
            return

        if (
            provider_metadata := provider.get_provider_metadata_from_prowjob(
                prowjob=job,
                gcs_client=self._client,
                gcs_bucket_name=self._gcs_bucket_name,
            )
        ) is None:
            logger.debug(
                "No provider metadata found for job %s with %s provider",
                job,
                provider.id,
            )
            return

        cir_metadata.region = provider_metadata.region
        cir_metadata.hostname = provider_metadata.hostname
        cir_metadata.os = provider_metadata.os
        job.cirMetadata = cir_metadata
