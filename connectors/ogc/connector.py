"""Conector OGC (WMS/WFS) para o BHGEO/BHMAP (GeoServer).

Pontos levantados no teste empírico (docs/03-implementacao/01-teste-apis.md):
- WFS 2.0.0 com 350 feature types, todos em DefaultCRS EPSG:31983.
- GetFeature devolve GeoJSON (outputFormat=application/json).
- Reprojeção server-side via srsName=urn:ogc:def:crs:EPSG::4326 — o GeoServer
  devolve as coordenadas já em WGS84, sem reprojeção cliente-side.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Optional

from connectors.base import BaseConnector, ConnectorError

BHGEO_WFS_URL = "https://bhmap.pbh.gov.br/v2/api/idebhgeo/wfs"
BHGEO_WMS_URL = "https://bhmap.pbh.gov.br/v2/api/idebhgeo/wms"

_WFS_NS = {
    "wfs": "http://www.opengis.net/wfs/2.0",
    "ows": "http://www.opengis.net/ows/1.1",
}
_WMS_NS = {"wms": "http://www.opengis.net/wms"}


def _srs_urn(srs: str) -> str:
    """Normaliza 'EPSG:4326' -> 'urn:ogc:def:crs:EPSG::4326' (formato OGC)."""
    if srs.startswith("urn:ogc:def:crs:"):
        return srs
    if srs.upper().startswith("EPSG:"):
        code = srs.split(":", 1)[1]
        return f"urn:ogc:def:crs:EPSG::{code}"
    return srs


class OgcConnector(BaseConnector):
    """Cliente OGC WFS/WMS (leitura)."""

    def __init__(
        self,
        wfs_url: str = BHGEO_WFS_URL,
        wms_url: str = BHGEO_WMS_URL,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.wfs_url = wfs_url
        self.wms_url = wms_url

    # ------------------------------------------------------------------
    # descoberta (GetCapabilities)
    # ------------------------------------------------------------------
    def capabilities(self, service: str = "WFS") -> dict:
        """Devolve o XML de GetCapabilities cru parseado (dict com tipo e itens)."""
        if service.upper() == "WFS":
            url = self.wfs_url
            params = {
                "service": "WFS",
                "request": "GetCapabilities",
                "version": "2.0.0",
            }
            return self._parse_wfs_capabilities(self._get_text(url, params=params))
        url = self.wms_url
        params = {
            "service": "WMS",
            "request": "GetCapabilities",
            "version": "1.3.0",
        }
        return self._parse_wms_capabilities(self._get_text(url, params=params))

    def feature_types(self) -> list[dict]:
        """Lista os feature types do WFS: [{name, title, crs}]."""
        return self._parse_wfs_capabilities(
            self._get_text(
                self.wfs_url,
                params={"service": "WFS", "request": "GetCapabilities", "version": "2.0.0"},
            )
        )["feature_types"]

    def _get_text(self, url: str, *, params: Optional[dict] = None) -> str:
        resp = self._request("GET", url, params=params)
        # O GetCapabilities é XML (texto), não JSON.
        return resp.text

    # ------------------------------------------------------------------
    # dados (GetFeature)
    # ------------------------------------------------------------------
    def get_feature(
        self,
        type_name: str,
        *,
        count: int = 100,
        start_index: int = 0,
        srs: str = "EPSG:4326",
        bbox: Optional[tuple[float, float, float, float]] = None,
        cql_filter: Optional[str] = None,
        properties: Optional[list[str]] = None,
    ) -> dict:
        """GetFeature -> GeoJSON FeatureCollection (dict).

        type_name: ex. 'ide_bhgeo:ACADEMIA_CIDADE'.
        srs: reprojeção server-side (padrão EPSG:4326/WGS84).
        bbox: (minx, miny, maxx, maxy) no CRS de 'srs'.
        cql_filter: filtro CQL do GeoServer (ex. "NOME LIKE '%CENTRO%'").
        properties: colunas a retornar (economiza payload).
        """
        params: dict[str, Any] = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": type_name,
            "outputFormat": "application/json",
            "srsName": _srs_urn(srs),
            "count": count,
            "startIndex": start_index,
        }
        if bbox is not None:
            # ordem OGC: minx,miny,maxx,maxy,crs
            params["bbox"] = ",".join(str(v) for v in bbox) + "," + _srs_urn(srs)
        if cql_filter:
            params["cql_filter"] = cql_filter
        if properties:
            params["propertyName"] = ",".join(properties)
        data = self._get_json(self.wfs_url, params=params)
        if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
            raise ConnectorError(
                f"GetFeature inesperado para '{type_name}': {str(data)[:200]}"
            )
        return data

    # ------------------------------------------------------------------
    # GetMap (WMS) — imagem raster
    # ------------------------------------------------------------------
    def get_map(
        self,
        layers: str,
        *,
        bbox: tuple[float, float, float, float],
        width: int = 800,
        height: int = 600,
        srs: str = "EPSG:4326",
        format: str = "image/png",
    ) -> bytes:
        """WMS GetMap -> bytes da imagem (PNG)."""
        params = {
            "service": "WMS",
            "version": "1.3.0",
            "request": "GetMap",
            "layers": layers,
            "bbox": ",".join(str(v) for v in bbox),
            "width": width,
            "height": height,
            "crs": srs,
            "format": format,
        }
        resp = self._request("GET", self.wms_url, params=params)
        return resp.content

    # ------------------------------------------------------------------
    # parsing
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_wfs_capabilities(xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        feature_types: list[dict] = []
        for ft in root.findall(".//wfs:FeatureType", _WFS_NS):
            name = ft.find("wfs:Name", _WFS_NS)
            title = ft.find("wfs:Title", _WFS_NS)
            crs = ft.find("wfs:DefaultCRS", _WFS_NS)
            feature_types.append(
                {
                    "name": name.text if name is not None else None,
                    "title": title.text if title is not None else None,
                    "crs": crs.text if crs is not None else None,
                }
            )
        return {"feature_types": feature_types, "total": len(feature_types)}

    @staticmethod
    def _parse_wms_capabilities(xml_text: str) -> dict:
        root = ET.fromstring(xml_text)
        layers: list[dict] = []
        for lyr in root.findall(".//wms:Layer", _WMS_NS):
            name = lyr.find("wms:Name", _WMS_NS)
            title = lyr.find("wms:Title", _WMS_NS)
            crs = lyr.find("wms:CRS", _WMS_NS)
            if name is None or name.text is None:
                continue
            layers.append(
                {
                    "name": name.text,
                    "title": title.text if title is not None else None,
                    "crs": crs.text if crs is not None else None,
                }
            )
        return {"layers": layers, "total": len(layers)}
