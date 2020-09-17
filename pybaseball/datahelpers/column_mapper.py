from collections import Counter
from typing import Callable, Iterator, List, Optional

ColumnListMapperFunction = Callable[[List[str]], Iterator[str]]

class GenericColumnMapper:
    def __init__(self):
        self.call_counts = Counter()

    def _short_circuit(self, column_name: str) -> Optional[str]:
        return None

    def map_list(self, column_names: List[str]) -> Iterator[str]:
        self.call_counts = Counter()
        for column_name in column_names:
            yield self.map(str(column_name))

    def map(self, column_name: str) -> str:
        self.call_counts[column_name] += 1
        # First time around use the actual column name
        if self.call_counts[column_name] == 1:
            return column_name

        # pylint: disable=assignment-from-none
        munged_value = self._short_circuit(column_name)
        # Just tack on a number for other calls
        return munged_value if munged_value is not None else f"{column_name} {self.call_counts[column_name]}"


class BattingStatsColumnMapper(GenericColumnMapper):
    def _short_circuit(self, column_name: str) -> Optional[str]:
        # Rename the second FB% column
        if column_name == "FB%" and self.call_counts[column_name] == 2:
            return "FB% (Pitch)"

        return None
