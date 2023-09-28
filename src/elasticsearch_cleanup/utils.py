from typing import Any, Iterator

from elasticsearch_cleanup.models import IndexFieldSelector


def get_value_from_dict(dot_notation_string: str, data: dict[str, Any]) -> Any:
    """Retrieves a value from a dictionary based on dot notation string.

    Args:
        dot_notation_string: The string in dot notation representing keys in the dictionary.
        data: The dictionary to extract data from.

    Returns:
        The value extracted from the dictionary based on the dot notation string.
    """
    keys = dot_notation_string.split(".")

    for key in keys:
        data = data[key]

    return data


def parse_index_and_fields_pairs(pairs: str) -> Iterator[IndexFieldSelector]:
    """Parses pairs of index and fields from a given string.

    The input string format should be 'index1: field1, field2 ; index2: field3, field4, field5 ; ...'.
    This function will convert the input string into a list of tuple pairs
    where each tuple represents (index, field).

    Args:
        pairs: The input string containing index-fields pairs separated by semicolon.

    Returns:
        A list of tuples where each tuple represents an index and its corresponding fields list.

    Example:
        >>> list(parse_index_and_fields_pairs("index1:field1, field2; index2:field3, field4, field5"))
        [('index1', ['field1', 'filed2']), ('index2', ['field3', 'field4', 'field5'])]
    """
    return (
        IndexFieldSelector(index=pair[0], field_selection=pair[1].split(","))
        for pair in (pair.split(":") for pair in pairs.replace(" ", "").split(";"))
    )
