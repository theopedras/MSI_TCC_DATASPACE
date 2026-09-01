"""Testes de integração — batem nas APIs reais das fontes.

Rodar com: pytest --integration
Não rodam por padrão (ver tests/conftest.py) para não sobrecarregar os servidores
públicos nem tornar o ciclo de desenvolvimento lento.

Cada teste valida um aspecto concreto da interoperabilidade entre fontes.
"""

from __future__ import annotations

import pytest

from connectors.ckan import CkanConnector
from connectors.gtfs import GtfsConnector
from connectors.ogc import OgcConnector
from connectors.rest import IbgeConnector
from dataspace import Dataspace

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# CKAN (PBH)
# ---------------------------------------------------------------------------
def test_ckan_catalogo_responde():
    c = CkanConnector()
    datasets = c.package_list()
    assert len(datasets) > 500  # 605 no levantamento


def test_ckan_datastore_consulta_inplace():
    c = CkanConnector()
    pkg = c.package_show("sinalizacao-semaforica")
    latest = c.latest_resource(pkg)
    assert latest is not None
    result = c.datastore_search(latest["id"], limit=5)
    assert result["total"] > 0
    assert len(result["records"]) <= 5


# ---------------------------------------------------------------------------
# BHGEO (OGC/WFS) — reprojeção SRID
# ---------------------------------------------------------------------------
def test_ogc_reprojeta_para_wgs84():
    c = OgcConnector()
    fc = c.get_feature("ide_bhgeo:ACADEMIA_CIDADE", count=1, srs="EPSG:4326")
    assert fc["crs"]["properties"]["name"] == "urn:ogc:def:crs:EPSG::4326"
    lon, lat = fc["features"][0]["geometry"]["coordinates"]
    # coordenadas dentro da área de Belo Horizonte (WGS84)
    assert -44.5 < lon < -43.0
    assert -20.5 < lat < -19.0


# ---------------------------------------------------------------------------
# IBGE (REST)
# ---------------------------------------------------------------------------
def test_ibge_populacao_bh():
    c = IbgeConnector()
    rows = c.dados_simples("6579", "2021", "9324", "3106200")
    assert rows and rows[0]["localidade_id"] == "3106200"
    populacao = float(rows[0]["valor"])
    assert 2_000_000 < populacao < 3_000_000


# ---------------------------------------------------------------------------
# GTFS-Realtime (protobuf)
# ---------------------------------------------------------------------------
def test_gtfs_realtime_veiculos():
    c = GtfsConnector()
    posicoes = c.vehicle_positions()
    assert len(posicoes) > 0
    assert -44.5 < posicoes[0]["longitude"] < -43.0


# ---------------------------------------------------------------------------
# Interoperabilidade cross-source (o coração do dataspace)
# ---------------------------------------------------------------------------
def test_interoperabilidade_academias_por_100k():
    """Junta BHGEO (OGC/WFS) com IBGE (REST) pelo município de BH."""
    ds = Dataspace()
    r = ds.academias_por_100k("2021")
    assert r["populacao"] > 2_000_000
    assert r["academias"] > 0
    assert 0 < r["academias_por_100k"] < 100


def test_interoperabilidade_veiculos_ativos():
    """Lê o feed GTFS-Realtime (protobuf) — protocolo distinto dos demais."""
    ds = Dataspace()
    r = ds.veiculos_ativos()
    assert r["veiculos_em_transito"] > 0
