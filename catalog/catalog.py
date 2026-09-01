"""Catálogo de metadados do dataspace (registro em memória).

Armazena Dataset (DCAT-like) colhidos pelos harvesters e permite busca simples.
"""

from __future__ import annotations

from typing import Iterator, Optional

from catalog.models import Dataset


class Catalog:
    def __init__(self) -> None:
        self._datasets: dict[str, Dataset] = {}

    def add(self, dataset: Dataset) -> None:
        self._datasets[dataset.identifier] = dataset

    def get(self, identifier: str) -> Optional[Dataset]:
        return self._datasets.get(identifier)

    def all(self) -> list[Dataset]:
        return list(self._datasets.values())

    def __len__(self) -> int:
        return len(self._datasets)

    def __iter__(self) -> Iterator[Dataset]:
        return iter(self._datasets.values())

    def search(self, query: str) -> list[Dataset]:
        """Busca por substring em título, descrição e palavras-chave."""
        q = query.lower()
        hits: list[Dataset] = []
        for ds in self._datasets.values():
            haystack = " ".join(
                [ds.title, ds.description or ""] + ds.keywords
            ).lower()
            if q in haystack:
                hits.append(ds)
        return hits
