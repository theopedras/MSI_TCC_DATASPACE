"""Harvester: colhe metadados de uma fonte e os converte em Dataset (DCAT)."""

from __future__ import annotations

from typing import Optional

from catalog.models import Dataset
from connectors.ckan import CkanConnector


class CkanHarvester:
    """Colhe datasets de um catálogo CKAN e converte para o modelo DCAT-like."""

    def __init__(self, connector: CkanConnector) -> None:
        self.connector = connector

    def harvest(self, dataset_id: str) -> Dataset:
        """Converte um dataset (package_show) em Dataset."""
        package = self.connector.package_show(dataset_id)
        return Dataset.from_ckan(package, source=self.connector.base_url)

    def harvest_all(self) -> list[Dataset]:
        """Colhe todos os datasets do catálogo (package_list -> package_show)."""
        return [self.harvest(name) for name in self.connector.package_list()]
