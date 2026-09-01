"""Orquestrador do dataspace: amarra conectores + catálogo + interoperabilidade.

Este é o "core" que materializa o princípio do TCC — os dados permanecem nas
fontes e são integrados sob demanda. O Dataspace consulta as APIs na hora de
responder, sem repositório central.

Demonstração de interoperabilidade real entre arquiteturas distintas:
  academias_por_100k() cruza uma camada OGC/WFS (BHGEO, reprojetada p/ WGS84)
  com população do IBGE (REST), unindo as duas pelo município (BH = 3106200).
"""

from __future__ import annotations

from typing import Any, Optional

from catalog import Catalog, CkanHarvester, Dataset
from connectors.ckan import CkanConnector
from connectors.gtfs import GtfsConnector
from connectors.ogc import OgcConnector
from connectors.rest import BH_IBGE_CODE, IbgeConnector, PncpConnector
from interoperability import normalize_ibge_code, per_100k, to_float

# Agregado 6579 = "População residente estimada", variável 9324.
_AGREGADO_POPULACAO = "6579"
_VARIAVEL_POPULACAO = "9324"


class Dataspace:
    """Ponto de entrada do dataspace de dados abertos (BH)."""

    def __init__(self) -> None:
        self.ckan = CkanConnector()
        self.ogc = OgcConnector()
        self.ibge = IbgeConnector()
        self.gtfs = GtfsConnector()
        self.pncp = PncpConnector()
        self.catalog = Catalog()
        self.ckan_harvester = CkanHarvester(self.ckan)

    # ------------------------------------------------------------------
    # catálogo
    # ------------------------------------------------------------------
    def harvest_ckan(self, limit: Optional[int] = None) -> int:
        """Colhe o catálogo CKAN da PBH para o catálogo DCAT do dataspace.

        Retorna o número de datasets colhidos. limit opcional (para testes).
        """
        ids = self.ckan.package_list()
        if limit is not None:
            ids = ids[:limit]
        for dataset_id in ids:
            self.catalog.add(self.ckan_harvester.harvest(dataset_id))
        return len(ids)

    # ------------------------------------------------------------------
    # consultas unificadas (camada de interoperabilidade)
    # ------------------------------------------------------------------
    def populacao(self, municipio: str = BH_IBGE_CODE, ano: str = "2021") -> int:
        """População residente estimada de um município (fonte: IBGE)."""
        municipio = normalize_ibge_code(municipio)
        rows = self.ibge.dados_simples(
            _AGREGADO_POPULACAO, [ano], _VARIAVEL_POPULACAO, municipio
        )
        if not rows:
            raise ValueError(f"sem população para {municipio} no ano {ano}")
        return int(to_float(rows[0]["valor"]))

    def camada_total(self, type_name: str) -> int:
        """Nº total de feições de uma camada do BHGEO (via totalFeatures do WFS).

        Reprojeção p/ WGS84 explícita: é a camada de interoperabilidade de SRID.
        """
        fc = self.ogc.get_feature(type_name, count=1, srs="EPSG:4326")
        return int(fc["totalFeatures"])

    def academias_por_100k(self, ano: str = "2021") -> dict[str, Any]:
        """Demonstração de interoperabilidade: academias da cidade por 100 mil hab.

        Cruza BHGEO (OGC/WFS) com IBGE (REST) pelo município de BH.
        """
        n_academias = self.camada_total("ide_bhgeo:ACADEMIA_CIDADE")
        populacao = self.populacao(BH_IBGE_CODE, ano)
        return {
            "municipio": BH_IBGE_CODE,
            "populacao": populacao,
            "ano": ano,
            "academias": n_academias,
            "academias_por_100k": round(per_100k(n_academias, populacao), 2),
            "fontes": ["BHGEO (WFS, reprojetado)", "IBGE (Agregados)"],
        }

    def veiculos_ativos(self) -> dict[str, Any]:
        """Demonstração de tempo real: veículos em trânsito agora (BHTRANS/GTFS-RT)."""
        posicoes = self.gtfs.vehicle_positions()
        return {
            "veiculos_em_transito": len(posicoes),
            "fonte": "BHTRANS (GTFS-Realtime, protobuf)",
        }
