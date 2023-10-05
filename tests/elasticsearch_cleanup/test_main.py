import json
from typing import Any
from unittest.mock import MagicMock, patch

import pkg_resources
import pytest

from elasticsearch_cleanup import main


@pytest.fixture(autouse=True)
def mock_config():
    with patch("elasticsearch_cleanup.main.config") as config:
        config.ES_URL = ""
        config.ES_USER = ""
        config.ES_PASSWORD = ""
        config.ES_INDEX_FIELDS_PAIRS = "jobs-*: job.build_id"
        config.DRY_RUN = "false"

        yield config


@pytest.fixture()
def job_documents() -> list[dict[str, Any]]:
    return json.loads(
        pkg_resources.resource_string(__name__, f"assets/job_assets.json")
    )


@pytest.fixture()
def step_documents() -> list[dict[str, Any]]:
    return json.loads(
        pkg_resources.resource_string(__name__, f"assets/step_assets.json")
    )


@pytest.fixture(autouse=True)
def mock_opensearch_helpers(job_documents) -> MagicMock:
    with patch("elasticsearch_cleanup.main.helpers") as os_helpers:
        os_helpers.scan.return_value = job_documents
        os_helpers.bulk.return_value = (len(job_documents), 0)
        yield os_helpers


@pytest.fixture(autouse=True)
def mock_opensearch_client() -> MagicMock:
    with patch("elasticsearch_cleanup.main.OpenSearch") as opensearch:
        yield opensearch()


def test_get_bulk_actions_with_compatibale_arguments_one_field_should_be_successfull(
    job_documents,
):
    bulk_actions = main.get_bulk_actions(job_documents, ["job.build_id"])

    assert len(list(bulk_actions)) == 2


def test_get_bulk_actions_with_compatibale_arguments_two_fields_should_be_successfull(
    step_documents,
):
    bulk_actions = main.get_bulk_actions(step_documents, ["job.build_id", "step.name"])

    assert len(list(bulk_actions)) == 1


def test_get_bulk_actions_with_incompatibale_arguments_should_be_successfull(
    job_documents,
):
    with pytest.raises(Exception):
        bulk_actions = main.get_bulk_actions(
            job_documents,
            ["job.build_id.missing_field"],
        )
        next(bulk_actions)


def test_full_flow_should_be_successfull(
    mock_opensearch_helpers, mock_opensearch_client
):
    main.main()

    mock_opensearch_helpers.scan.assert_called_once()
    mock_opensearch_helpers.bulk.assert_called_once()
    mock_opensearch_client.indices.refresh.assert_called_once()


def test_dry_run_flow_should_be_successfull(
    mock_opensearch_helpers, mock_opensearch_client, mock_config
):
    mock_config.DRY_RUN = "true"

    main.main()

    mock_opensearch_helpers.scan.assert_called_once()
    mock_opensearch_helpers.bulk.assert_not_called()
    mock_opensearch_client.indices.refresh.assert_not_called()
