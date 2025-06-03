import logging
from typing import List, Optional

from google.cloud import exceptions, storage  # type: ignore
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from providers.common import (
    PROVIDER_METADATA_PATH_TEMPLATE,
    Provider,
    ProviderMetadata,
)
from prowjobsscraper import utils
from prowjobsscraper.prowjob import ProwJob


class ProviderAWSMetadata(BaseModel):
    imageId: str
    instanceId: str
    region: str


class ProviderAWS(Provider):
    _id: str = "aws"

    def get_provider_metadata_from_prowjob(
        self, prowjob: ProwJob, gcs_client: storage.Client, gcs_bucket_name: str
    ) -> Optional[ProviderMetadata]:
        base_path = utils.get_gcs_base_path_from_job_url(prowjob.status.url)
        metadata_path = PROVIDER_METADATA_PATH_TEMPLATE.format(
            base_path, prowjob.context, self._id
        )

        try:
            raw_metadata = utils.download_from_gcs_as_string(
                gcs_client, gcs_bucket_name, metadata_path
            )
            if raw_metadata is None:
                logger.debug("AWS metadata is empty: %s", metadata_path)
                return None

            logger.debug("Found AWS metadata at: %s", metadata_path)
        except exceptions.ClientError as e:
            logger.debug("AWS metadata is missing from %s: %s", metadata_path, e)
            return None

        try:
            aws_instance_metadata = ProviderAWSMetadata.parse_raw(raw_metadata)
            logger.debug("Decoded AWS metadata successfully from: %s", metadata_path)
        except Exception as e:
            logger.warning(
                f"Failed to decode AWS metadata for job {prowjob.spec.job}: {e}"
            )
            return None

        return ProviderMetadata(
            region=aws_instance_metadata.region,
            hostname=aws_instance_metadata.instanceId,
            os=aws_instance_metadata.imageId,
        )
