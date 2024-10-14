"""This script is used for removing duplicate documents from OpenSearch indices.

The main logic includes:
1. Setting up the OpenSearch client.
2. Fetching all documents from specified OpenSearch indices.
3. Identifying duplicate documents based on comparison fields.
4. Removing the duplicates if not in dry-run mode or logging the bulk actions if in dry-run mode.

This scripts assumes:
1. fields name doesn't contain any of ';', ':', ',', '.'.
2. '_source' field is Elasticsearch is enabled.
"""

import json
from typing import Any, Iterator

from opensearchpy import OpenSearch, helpers

from elasticsearch_cleanup import config, consts
from elasticsearch_cleanup.logger import get_logger
from elasticsearch_cleanup.models import IndexFieldSelector
from elasticsearch_cleanup.utils import (
    get_value_from_dict,
    parse_index_and_fields_pairs,
)

logger = get_logger(config.LOG_LEVEL)


def remove_documents(
    opensearch_client: OpenSearch,
    actions: Iterator[dict[str, str]],
    index: str,
):
    """Removes specified documents from the OpenSearch index.

    Args:
        opensearch_client: The client to communicate with OpenSearch.
        actions: List of actions to remove documents.
        index: The name of the index.
    """
    successes, failures = helpers.bulk(
        client=opensearch_client,
        actions=actions,
        stats_only=True,
    )

    opensearch_client.indices.refresh(index=index)

    logger.info(f"Number of successfull deletions: '{successes}'")
    logger.info(f"number of failing deletions: '{failures}'")


def get_bulk_actions(
    documents: Iterator[dict[str, Any]],
    comparison_fields: list[str],
) -> Iterator[dict[str, str]]:
    """Generates bulk actions for documents based on a comparison fields.

    Args:
        documents: Iterable documents to be compared.
        comparison_fields: List of fields for comparison to identify unique documents.

    Yields:
        Bulk action for the documents.
    """
    seen_values = set()

    for doc in documents:
        unique_fields_value = tuple(
            get_value_from_dict(
                dot_notation_string=field,
                data=doc["_source"],
            )
            for field in comparison_fields
        )

        if unique_fields_value in seen_values:
            yield {
                "_op_type": "delete",
                "_index": doc["_index"],
                "_id": doc["_id"],
            }

        else:
            seen_values.add(unique_fields_value)


def remove_duplicates_from_index(
    opensearch_client: OpenSearch,
    index: str,
    comparison_fields: list[str],
    dry_run_mode: bool,
) -> None:
    """Removes duplicates from an OpenSearch index based on a specified comparison field.

    This function retrieves all documents from a given OpenSearch index, identifies
    duplicates based on the provided comparison fields, and removes them. The function
    supports a dry run mode where it logs the potential actions without actually
    executing the removal of duplicates.

    Args:
        opensearch_client: The client to communicate with OpenSearch.
        index: The name of the OpenSearch index.
        comparison_fields: List of fields in the document to use for identifying duplicates.
        dry_run_mode: If set to True, the function will only log the potential
                      removal actions without actually deleting any documents.
    """
    logger.info(
        f"Processing index '{index}' with comparison fields '{comparison_fields}'"
    )

    documents: Iterator = helpers.scan(
        opensearch_client,
        index=index,
        query=consts.OPENSEARCH_QUERY_ALL_INDEX_DOCUMENTS,
        ignore_unavailable=True,
    )

    bulk_actions = get_bulk_actions(
        documents=documents,
        comparison_fields=comparison_fields,
    )

    if dry_run_mode:
        logger.info(f"Bulk Actions in '{index}':")
        for action in bulk_actions:
            logger.info(json.dumps(action, indent=4))

        return

    remove_documents(
        opensearch_client=opensearch_client,
        actions=bulk_actions,
        index=index,
    )


def get_latest_index(opensearch_client: OpenSearch, index_pattern: str) -> str:
    """Retrieves the latest non-empty OpenSearch index for a given index pattern

    Args:
        opensearch_client: The client to communicate with OpenSearch.
        index_pattern: The name of the OpenSearch index pattern to take the latest from.

    Returns:
        The latest non-empty OpenSearch index matching the given pattern.
    """
    indices = opensearch_client.cat.indices(
        index=index_pattern, format="json", h="index,docs.count"
    )
    non_empty_indices = [index for index in indices if int(index["docs.count"]) > 0]
    sorted_non_empty_indices = sorted(
        non_empty_indices, reverse=True, key=lambda map: map["index"]
    )
    if len(sorted_non_empty_indices) == 0:
        raise ValueError(
            f"ES_INDEX_LATEST is set to 'true' but {index_pattern} does not match any index"
        )

    return sorted_non_empty_indices[0]["index"]


def main() -> None:
    if (
        config.ES_INDEX_FIELDS_PAIRS is None
        or config.ES_URL is None
        or config.ES_USER is None
        or config.ES_PASSWORD is None
    ):
        raise ValueError("failed to get all required environment variables")

    opensearch_client = OpenSearch(
        config.ES_URL,
        http_auth=(config.ES_USER, config.ES_PASSWORD),
        verify_certs=False,
        ssl_show_warn=False,
    )

    index_field_selectors = parse_index_and_fields_pairs(
        pairs=config.ES_INDEX_FIELDS_PAIRS
    )

    if config.ES_INDEX_LATEST == "true":
        index_field_selectors = (
            IndexFieldSelector(
                index=get_latest_index(
                    opensearch_client=opensearch_client, index_pattern=selector.index
                ),
                field_selection=selector.field_selection,
            )
            for selector in index_field_selectors
        )

    dry_run_mode = not (config.DRY_RUN == "false")

    for index_field_selector in index_field_selectors:
        remove_duplicates_from_index(
            opensearch_client=opensearch_client,
            index=index_field_selector.index,
            comparison_fields=index_field_selector.field_selection,
            dry_run_mode=dry_run_mode,
        )


if __name__ == "__main__":
    main()
