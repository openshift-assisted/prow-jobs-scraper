from typing import Any
from unittest.mock import MagicMock, patch

from prowjobsscraper.equinix_usages import EquinixUsagesExtractor


@patch("prowjobsscraper.equinix_usages.requests")
def test_get_project_usages(requests: MagicMock):
    response_usages: dict[str, list[dict[str, Any]]] = {
        "usages": [
            {
                "description": None,
                "end_date": "2023-03-31T23:59:59Z",
                "facility": "dc13",
                "metro": "dc",
                "name": "ipi-ci-op-nnk50j82-5ed26-1634705984507088896",
                "plan": "Outbound Bandwidth",
                "plan_version": "Outbound Bandwidth",
                "price": 0.05,
                "quantity": 2,
                "start_date": "2023-03-01T00:00:00Z",
                "total": 0.1,
                "type": "Instance",
                "unit": "GB",
            },
            {
                "description": None,
                "end_date": "2023-03-31T23:59:59Z",
                "facility": "am6",
                "metro": "am",
                "name": "ipi-ci-op-tb33cyhd-20a45-1638140834400440320",
                "plan": "Outbound Bandwidth",
                "plan_version": "Outbound Bandwidth",
                "price": 0.05,
                "quantity": 4,
                "start_date": "2023-03-01T00:00:00Z",
                "total": 0.2,
                "type": "Instance",
                "unit": "GB",
            },
            {
                "description": None,
                "facility": "dc13",
                "metro": "dc",
                "name": "ipi-ci-op-3i64pdkt-0f69d-1633695483341836288",
                "plan": "Outbound Bandwidth",
                "plan_version": "Outbound Bandwidth",
                "price": 0.05,
                "quantity": 3,
                "start_date": "2023-03-01T00:00:00Z",
                "total": 0.15,
                "type": "Instance",
                "unit": "GB",
            },
        ]
    }

    requests.get.return_value.json.return_value = response_usages
    equinix = EquinixUsagesExtractor(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    usages = equinix.get_project_usages()

    assert len(usages) == 3
