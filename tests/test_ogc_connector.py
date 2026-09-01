"""Testes do OgcConnector (sem rede)."""

from unittest.mock import Mock

import pytest

from connectors.base import ConnectorError
from connectors.ogc import OgcConnector
from connectors.ogc.connector import _srs_urn

WFS_CAP_XML = """<?xml version="1.0"?>
<wfs:WFS_Capabilities version="2.0.0" xmlns:wfs="http://www.opengis.net/wfs/2.0"
    xmlns:ows="http://www.opengis.net/ows/1.1">
  <wfs:FeatureTypeList>
    <wfs:FeatureType>
      <wfs:Name>ide_bhgeo:ACADEMIA_CIDADE</wfs:Name>
      <wfs:Title>Academia da Cidade</wfs:Title>
      <wfs:DefaultCRS>urn:ogc:def:crs:EPSG::31983</wfs:DefaultCRS>
    </wfs:FeatureType>
    <wfs:FeatureType>
      <wfs:Name>ide_bhgeo:ADE_11181</wfs:Name>
      <wfs:Title>Ade Lei 11181</wfs:Title>
      <wfs:DefaultCRS>urn:ogc:def:crs:EPSG::31983</wfs:DefaultCRS>
    </wfs:FeatureType>
  </wfs:FeatureTypeList>
</wfs:WFS_Capabilities>
"""

WMS_CAP_XML = """<?xml version="1.0"?>
<WMS_Capabilities version="1.3.0" xmlns="http://www.opengis.net/wms">
  <Capability>
    <Layer>
      <Name>MAPA_BASE</Name>
      <Title>Mapa Base Belo Horizonte</Title>
      <CRS>EPSG:31983</CRS>
    </Layer>
    <Layer>
      <Name>ACADEMIA_CIDADE</Name>
      <Title>Academia da Cidade</Title>
      <CRS>EPSG:31983</CRS>
    </Layer>
  </Capability>
</WMS_Capabilities>
"""


def test_srs_urn_normaliza_epsg():
    assert _srs_urn("EPSG:4326") == "urn:ogc:def:crs:EPSG::4326"
    assert _srs_urn("urn:ogc:def:crs:EPSG::4326") == "urn:ogc:def:crs:EPSG::4326"


def test_parse_wfs_capabilities():
    parsed = OgcConnector._parse_wfs_capabilities(WFS_CAP_XML)
    assert parsed["total"] == 2
    assert parsed["feature_types"][0]["name"] == "ide_bhgeo:ACADEMIA_CIDADE"
    assert parsed["feature_types"][0]["crs"] == "urn:ogc:def:crs:EPSG::31983"


def test_parse_wms_capabilities():
    parsed = OgcConnector._parse_wms_capabilities(WMS_CAP_XML)
    assert parsed["total"] == 2
    assert parsed["layers"][0]["name"] == "MAPA_BASE"


def test_get_feature_monta_parametros_e_devolve_geojson():
    c = OgcConnector()
    captured = {}

    def fake_get_json(url, params=None):
        captured["url"] = url
        captured["params"] = params
        return {"type": "FeatureCollection", "features": []}

    c._get_json = Mock(side_effect=fake_get_json)
    c.get_feature(
        "ide_bhgeo:ACADEMIA_CIDADE",
        count=10,
        bbox=(-44.0, -20.0, -43.8, -19.8),
        cql_filter="NOME LIKE '%CENTRO%'",
    )
    p = captured["params"]
    assert p["typeNames"] == "ide_bhgeo:ACADEMIA_CIDADE"
    assert p["outputFormat"] == "application/json"
    assert p["srsName"] == "urn:ogc:def:crs:EPSG::4326"
    assert p["count"] == 10
    assert p["cql_filter"] == "NOME LIKE '%CENTRO%'"
    assert p["bbox"] == "-44.0,-20.0,-43.8,-19.8,urn:ogc:def:crs:EPSG::4326"


def test_get_feature_levanta_quando_resposta_nao_eh_feature_collection():
    c = OgcConnector()
    c._get_json = Mock(return_value={"error": "xpto"})
    with pytest.raises(ConnectorError):
        c.get_feature("ide_bhgeo:X")


def test_get_map_devolve_bytes():
    c = OgcConnector()
    resp = Mock()
    resp.content = b"PNGDATA"
    c._request = Mock(return_value=resp)
    out = c.get_map("MAPA_BASE", bbox=(-44, -20, -43, -19))
    assert out == b"PNGDATA"
    assert c._request.call_args.kwargs["params"]["format"] == "image/png"
