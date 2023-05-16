from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

from prowjobsscraper.equinix_usages import EquinixUsagesExtractor


@patch("prowjobsscraper.equinix_usages.requests")
def test_get_project_usages(requests: MagicMock):
    response_usages: dict[str, list[dict[str, Any]]] = {
        "usages": [
            {
                "description": None,
                "facility": "da11",
                "metro": "da",
                "name": "ipi-ci-op-nnk50j82-5ed26-1634705984507088896",
                "plan": "c3.medium.x86",
                "plan_version": "c3.medium.x86 v2 (Dell EPYC 7402P)",
                "price": 1.5,
                "quantity": 2.0,
                "total": 3.0,
                "type": "Instance",
                "unit": "hour",
                "start_date": "2023-03-20T07:56:49Z",
                "end_date": "2023-03-20T09:51:49Z",
            },
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
                "end_date": "2023-03-30T00:00:00Z",
                "total": 0.1,
                "type": "Instance",
                "unit": "GB",
            },
            {
                "description": None,
                "facility": "dc13",
                "metro": "dc",
                "name": "ipi-ci-op-nnk50j82-5ed26-1634705984507088896",
                "plan": "Backend Transfer Bandwidth",
                "plan_version": "Backend Transfer Bandwidth",
                "price": 0.05,
                "quantity": 3,
                "start_date": "2023-03-01T00:00:00Z",
                "end_date": "2023-03-30T00:00:00Z",
                "total": 0.15,
                "type": "Instance",
                "unit": "GB",
            },
            {
                "description": None,
                "facility": "dc13",
                "metro": "dc",
                "name": "ipi-ci-op-qbtg69w9-88355-1648876148169379840",
                "plan": "c3.small.x86",
                "plan_version": "c3.small.x86 v1",
                "price": 0.75,
                "quantity": 1.0,
                "total": 0.75,
                "type": "Instance",
                "unit": "hour",
                "start_date": "2023-03-21T00:00:00Z",
                "end_date": "2023-03-21T02:00:00Z",
            },
            {
                "description": None,
                "facility": "dc13",
                "metro": "dc",
                "name": "ipi-ci-op-qbtg69w9-88355-1234576148169312345",
                "plan": "c3.small.x86",
                "plan_version": "c3.small.x86 v1",
                "price": 0.75,
                "quantity": 1.0,
                "total": 0.75,
                "type": "Instance",
                "unit": "hour",
                "start_date": "2023-03-21T00:00:00Z",
            },
        ]
    }

    requests.get.return_value.json.return_value = response_usages
    start_time = datetime(
        year=2023, month=3, day=20, hour=5, minute=0, second=0, tzinfo=timezone.utc
    )
    end_time = datetime(
        year=2023, month=3, day=20, hour=11, minute=0, second=0, tzinfo=timezone.utc
    )
    equinix = EquinixUsagesExtractor(MagicMock(), MagicMock(), start_time, end_time)
    usages = equinix.get_project_usages()

    assert len(usages) == 3
    assert (
        len(
            [
                usage
                for usage in usages
                if usage.start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                == "2023-03-20T07:56:49Z"
                and usage.end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                == "2023-03-20T09:51:49Z"
            ]
        )
        == 3
    )
