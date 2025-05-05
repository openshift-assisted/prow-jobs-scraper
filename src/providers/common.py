from abc import ABC, abstractmethod
from typing import Final, Optional

from google.cloud import storage  # type: ignore
from pydantic import BaseModel

from prowjobsscraper.prowjob import ProwJob

PROVIDER_METADATA_PATH_TEMPLATE: Final[str] = (
    "{}/artifacts/{}/ofcir-gather/artifacts/{}-metadata.json"
)


class ProviderMetadata(BaseModel):
    region: str
    hostname: str
    os: str


class Provider(ABC, BaseModel):
    _id: str

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def get_provider_metadata_from_prowjob(
        self, prowjob: ProwJob, gcs_client: storage.Client, gcs_bucket_name: str
    ) -> Optional[ProviderMetadata]:
        pass
