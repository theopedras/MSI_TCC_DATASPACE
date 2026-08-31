"""Conector CKAN (PBH e MG)."""

from connectors.ckan.connector import (
    MG_BASE_URL,
    PBH_BASE_URL,
    CkanConnector,
)

__all__ = ["CkanConnector", "PBH_BASE_URL", "MG_BASE_URL"]
