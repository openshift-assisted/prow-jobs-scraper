from dataclasses import dataclass


@dataclass
class IndexFieldSelector:
    index: str
    field_selection: list[str]
