import logging
from typing import Optional

from google.cloud import exceptions, storage  # type: ignore
from pydantic import BaseModel

logger = logging.getLogger(__name__)


from providers.common import (
    PROVIDER_METADATA_PATH_TEMPLATE,
    Provider,
    ProviderMetadata,
)
from prowjobsscraper import utils
from prowjobsscraper.prowjob import ProwJob


class ProviderEquinixOSMetadata(BaseModel):
    slug: str


class ProviderEquinixMetadata(BaseModel):
    hostname: str
    metro: str
    operating_system: ProviderEquinixOSMetadata


class ProviderEquinix(Provider):
    _id: str = "equinix"

    def get_provider_metadata_from_prowjob(
        self, prowjob: ProwJob, gcs_client: storage.Client, gcs_bucket_name: str
    ) -> Optional[ProviderMetadata]:
        base_path = utils.get_gcs_base_path_from_job_url(prowjob.status.url)
        metadata_path = PROVIDER_METADATA_PATH_TEMPLATE.format(
            base_path, prowjob.context, self._id
        )
        try:
            if (
                raw_metadata := utils.download_from_gcs_as_string(
                    gcs_client, gcs_bucket_name, metadata_path
                )
            ) is None:
                logger.debug("Metadata is empty: %s", metadata_path)
                return None
            logger.debug("Found metadata: %s", metadata_path)
        except exceptions.ClientError as e:
            logger.debug("Metadata is missing from %s: %s", metadata_path, e)
            return None

        try:
            equinix_instance_metadata = ProviderEquinixMetadata.parse_raw(raw_metadata)
            logger.debug("Decoded successfully Equinix metadata in: %s", metadata_path)
        except Exception as e:
            logger.warning(
                f"Failed to decode Equinix metadata for job {prowjob.spec.job}: {e}"
            )
            return None

        return ProviderMetadata(
            region=equinix_instance_metadata.metro,
            hostname=equinix_instance_metadata.hostname,
            os=equinix_instance_metadata.operating_system.slug,
        )
