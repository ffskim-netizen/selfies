"""A minimal subset of the :mod:`pandas` API used in the tests.

This lightweight implementation provides just enough functionality for the
unit tests to exercise the :mod:`selfies` package without pulling in the real
pandas dependency, which is not available in the execution environment.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Sequence
import csv


@dataclass
class _Series:
    """A tiny stand-in for :class:`pandas.Series`."""

    _values: List[str]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)


class DataFrame:
    """Minimal DataFrame supporting column access used in the tests."""

    def __init__(self, columns: Sequence[str], rows: Sequence[Sequence[str]]):
        self._columns = list(columns)
        self._data = {name: [] for name in self._columns}
        for row in rows:
            for idx, name in enumerate(self._columns):
                value = row[idx] if idx < len(row) else ""
                self._data[name].append(value)

    def __getitem__(self, key: str) -> _Series:
        return _Series(list(self._data[key]))


def _generate_chunks(
    columns: Sequence[str],
    rows: Iterable[Sequence[str]],
    chunksize: int,
) -> Iterator[DataFrame]:
    batch: List[Sequence[str]] = []
    for row in rows:
        batch.append(row)
        if len(batch) == chunksize:
            yield DataFrame(columns, batch)
            batch = []
    if batch:
        yield DataFrame(columns, batch)


def read_csv(
    path: str,
    *,
    chunksize: int | None = None,
    header: int | None = 0,
    skiprows: Iterable[int] | None = None,
):
    """Return an iterator over CSV chunks matching the limited test usage."""

    if header not in (0, None):
        raise ValueError("Only a single header row is supported in the stub")

    skip = set(skiprows or [])

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            columns = next(reader)
        except StopIteration as exc:  # pragma: no cover - defensive guard
            raise ValueError("CSV file is empty") from exc

        data_rows: List[List[str]] = []
        for line_number, row in enumerate(reader, start=1):
            if line_number in skip:
                continue
            data_rows.append(row)

    if chunksize is None:
        return DataFrame(columns, data_rows)

    return _generate_chunks(columns, data_rows, chunksize)
