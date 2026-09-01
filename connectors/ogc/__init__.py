"""Conector OGC (WMS/WFS) do BHGEO/BHMAP."""

from connectors.ogc.connector import (
    BHGEO_WFS_URL,
    BHGEO_WMS_URL,
    OgcConnector,
)

__all__ = ["OgcConnector", "BHGEO_WFS_URL", "BHGEO_WMS_URL"]
