import pytest

from elasticsearch_cleanup.models import IndexFieldSelector
from elasticsearch_cleanup.utils import (
    get_value_from_dict,
    parse_index_and_fields_pairs,
)


def test_get_value_from_dict_valid_keys():
    dictionary = {"a": {"b": {"c": "value"}}}

    assert get_value_from_dict("a.b.c", dictionary) == "value"


def test_get_value_from_dict_invalid_keys():
    dictionary = {"a": {"b": {"c": "value"}}}

    with pytest.raises(KeyError):
        get_value_from_dict("a.b.d", dictionary)


def test_parse_index_and_fields_pairs():
    pairs_string = (
        "index1:    field1, field2   ;    index2   :field3,     field4,   field5"
    )
    pairs_string_2 = "index1: field1, field2; index2: field3, field4, field5"

    expected = [
        IndexFieldSelector("index1", ["field1", "field2"]),
        IndexFieldSelector("index2", ["field3", "field4", "field5"]),
    ]

    assert list(parse_index_and_fields_pairs(pairs_string)) == expected
    assert list(parse_index_and_fields_pairs(pairs_string_2)) == expected
