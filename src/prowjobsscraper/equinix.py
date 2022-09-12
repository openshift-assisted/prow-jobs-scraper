import logging
from typing import Final, Optional

from google.cloud import exceptions, storage  # type: ignore

from prowjobsscraper import utils
from prowjobsscraper.prowjob import EquinixMetadata, ProwJob, ProwJobs

logger = logging.getLogger(__name__)


class EquinixExtractor:
    """
    EquinixExtractor parses the Equinix metadata generated by the gather step in assisted-baremetal, assisted-baremetal-operator and baremetalds-sno workflows.
    """

    # map cloud cluster profile with the possible locations of the equinix metadata file
    _METADATA_PATH_TEMPLATES: Final[dict[str, list[str]]] = {
        "packet-assisted": [
            "{}/artifacts/{}/baremetalds-packet-gather-metadata/artifacts/equinix-metadata.json",
            "{}/artifacts/{}/assisted-baremetal-gather/artifacts/equinix-metadata.json",
            "{}/artifacts/{}/assisted-baremetal-operator-gather/artifacts/equinix-metadata.json",
            "{}/artifacts/{}/assisted-common-gather/artifacts/equinix-metadata.json",
        ],
        "packet-sno": [
            "{}/artifacts/{}/baremetalds-packet-gather-metadata/artifacts/equinix-metadata.json",
            "{}/artifacts/{}/baremetalds-sno-gather/artifacts/equinix-metadata.json",
        ],
    }

    def __init__(self, client: storage.Client):
        self._client = client

    def hydrate(self, jobs: ProwJobs) -> None:
        for job in jobs.items:
            self._set_equinix_metadata(job)

    def _set_equinix_metadata(self, job: ProwJob) -> None:
        if job.metadata.labels.cloudClusterProfile not in self._METADATA_PATH_TEMPLATES:
            return

        bucket, base_path = utils.get_gcs_bucket_and_base_path_from_job_url(
            job.status.url
        )

        raw_metadata = None
        for path in self._METADATA_PATH_TEMPLATES[
            job.metadata.labels.cloudClusterProfile
        ]:
            metadata_path = path.format(base_path, job.context)

            try:
                raw_metadata = utils.download_from_gcs_as_string(
                    self._client, bucket, metadata_path
                )

                logger.debug("Found equinix metadata: %s", metadata_path)
                break

            except exceptions.ClientError as e:
                logger.debug(
                    "Equinix metadata are missing from %s: %s", metadata_path, e
                )
                continue

        if raw_metadata:
            job.equinixMetadata = EquinixMetadata.parse_raw(raw_metadata)
        else:
            logger.info("No equinix metadata found for job %s", job)
