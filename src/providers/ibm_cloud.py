import logging
from typing import Optional

from google.cloud import exceptions, storage  # type: ignore
from pydantic import BaseModel

from providers.common import (
    PROVIDER_METADATA_PATH_TEMPLATE,
    Provider,
    ProviderMetadata,
)
from prowjobsscraper import utils
from prowjobsscraper.prowjob import ProwJob

logger = logging.getLogger(__name__)


class ProviderMetadataOperatingSystem(BaseModel):
    fullyQualifiedDomainName: str


class ProviderMetadataOperatingSoftwareDescription(BaseModel):
    longDescription: str


class ProviderMetadataOperatingSoftwareLicense(BaseModel):
    softwareDescription: ProviderMetadataOperatingSoftwareDescription


class ProviderMetadataOperatingOperatingSystem(BaseModel):
    softwareLicense: ProviderMetadataOperatingSoftwareLicense


class ProviderIBMCloudMetadata(BaseModel):
    datacenter: str
    hardware: ProviderMetadataOperatingSystem
    operatingSystem: ProviderMetadataOperatingOperatingSystem


class ProviderIBMCloud(Provider):
    _id: str = "ibm-classic"

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
            ibm_cloud_instance_metadata = ProviderIBMCloudMetadata.parse_raw(
                raw_metadata
            )
            logger.debug(
                "Decoded successfully IBM Cloud metadata in: %s", metadata_path
            )
        except Exception as e:
            logger.warning(
                f"Failed to decode IBM Cloud metadata for job {prowjob.spec.job}: {e}"
            )
            return None

        return ProviderMetadata(
            region=ibm_cloud_instance_metadata.datacenter,
            hostname=ibm_cloud_instance_metadata.hardware.fullyQualifiedDomainName,
            os=ibm_cloud_instance_metadata.operatingSystem.softwareLicense.softwareDescription.longDescription,
        )
