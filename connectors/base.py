"""Classes base dos conectores do dataspace.

Responsabilidades comuns a todos os conectores: sessão HTTP com
impersonação de navegador (TLS fingerprint), User-Agent, timeout, retry
com backoff exponencial e tratamento de erros.

POR QUE curl_cffi e não requests:
  O WAF "gocache" da PBH bloqueia por fingerprint TLS (JA3), não apenas por
  User-Agent. O cliente TLS do Python (requests/urllib3) é reconhecido e
  recebe 403 mesmo com User-Agent de navegador. curl_cffi impersona o TLS de
  navegadores reais (chrome/safari/firefox) e passa. Ver
  docs/03-implementacao/01-teste-apis.md.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from curl_cffi import requests as http

# Usado junto com a impersonação de TLS. O sufixo identifica o cliente do
# dataspace (boa prática). O valor imita um navegador real.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
    "dataspace-bh-tcc/0.1"
)

DEFAULT_IMPERSONATE = "chrome"

# Códigos que indicam falha transitória (vale tentar de novo).
_RETRYABLE_STATUS = (408, 425, 429, 500, 502, 503, 504)


class ConnectorError(Exception):
    """Falha genérica de um conector."""


class AuthenticationError(ConnectorError):
    """Acesso negado (403/401) — credencial ausente, inválida ou bloqueio por WAF."""


class NotFoundError(ConnectorError):
    """Recurso não encontrado (404)."""


class ServerError(ConnectorError):
    """Falha transitória/definitiva no servidor (5xx, 429, timeout)."""


class BaseConnector:
    """Base para conectores HTTP: sessão + impersonação + retry + erros."""

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        impersonate: str = DEFAULT_IMPERSONATE,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff: float = 1.0,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self.session = http.Session(impersonate=impersonate)
        self.session.headers.update(
            {"User-Agent": user_agent, "Accept": "application/json"}
        )

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        **kwargs: Any,
    ):
        """Faz a requisição com retry em falhas transitórias."""
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.request(
                    method, url, params=params, timeout=self.timeout, **kwargs
                )
            except (http.exceptions.Timeout, http.exceptions.ConnectionError) as exc:
                last_exc = exc
            else:
                if resp.status_code < 400:
                    return resp
                if resp.status_code in (401, 403):
                    raise AuthenticationError(
                        f"{resp.status_code} em {url}: acesso negado (WAF/credencial/"
                        f"User-Agent). Resposta: {resp.text[:200]}"
                    )
                if resp.status_code == 404:
                    raise NotFoundError(f"404 em {url}")
                if resp.status_code in _RETRYABLE_STATUS:
                    last_exc = ServerError(
                        f"{resp.status_code} em {url} (tentativa {attempt + 1})"
                    )
                else:
                    raise ConnectorError(
                        f"{resp.status_code} em {url}: {resp.text[:200]}"
                    )
            if attempt < self.max_retries:
                time.sleep(self.backoff * (2 ** attempt))
        raise ConnectorError(
            f"falha após {self.max_retries + 1} tentativas em {url}"
        ) from last_exc

    def _get_json(self, url: str, *, params: Optional[dict] = None) -> Any:
        resp = self._request("GET", url, params=params)
        return resp.json()
