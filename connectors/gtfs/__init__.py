"""Conector GTFS (estático + tempo real) da BHTRANS."""

from connectors.gtfs.connector import (
    GTFS_RT_URLS,
    GTFS_STATIC_URL,
    GtfsConnector,
)

__all__ = ["GtfsConnector", "GTFS_STATIC_URL", "GTFS_RT_URLS"]
