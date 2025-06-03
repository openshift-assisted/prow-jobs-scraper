import logging
from typing import Optional

from providers.aws import ProviderAWS
from providers.common import Provider
from providers.equinix import ProviderEquinix
from providers.ibm_cloud import ProviderIBMCloud

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS: tuple[Provider, Provider, Provider] = (
    ProviderIBMCloud(),
    ProviderEquinix(),
    ProviderAWS(),
)


def get_provider_by_id(id: str) -> Optional[Provider]:
    return next((p for p in SUPPORTED_PROVIDERS if p.id == id), None)
