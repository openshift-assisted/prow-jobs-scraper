from typing import Any, Final

OPENSEARCH_QUERY_ALL_INDEX_DOCUMENTS: Final[dict[str, Any]] = {
    "query": {"match_all": {}},
    "sort": [
        {
            "_script": {
                "type": "number",
                "script": {"source": "doc['_id'].value.length()", "lang": "painless"},
                "order": "asc",
            }
        }
    ],
}
