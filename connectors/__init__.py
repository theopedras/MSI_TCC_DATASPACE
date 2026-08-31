"""Pacote de conectores do dataspace de dados abertos (BH)."""

from connectors.base import (
    DEFAULT_USER_AGENT,
    AuthenticationError,
    BaseConnector,
    ConnectorError,
    NotFoundError,
    ServerError,
)

__all__ = [
    "DEFAULT_USER_AGENT",
    "AuthenticationError",
    "BaseConnector",
    "ConnectorError",
    "NotFoundError",
    "ServerError",
]
