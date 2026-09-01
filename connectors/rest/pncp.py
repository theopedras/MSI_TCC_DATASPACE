"""Conector REST do PNCP (Portal Nacional de Contratações Públicas).

Fonte regulatória (Lei 14.133/2021) de licitações/contratos de TODOS os entes,
inclusive PBH e suas empresas (filtro por CNPJ do órgão).

Situação empírica (docs/03-implementacao/01-teste-apis.md):
- Endpoints verificados: /v1/orgaos e /v1/orgaos/{cnpj} (retornaram 504/timeout,
  o que confirma que o caminho existe; o backend é que está instável).
- A API de consulta é pública (sem auth); a de escrita (/api/pncp) usa JWT e
  está fora do escopo (só leitura interessa ao dataspace).
- O backend é lento/instável: recomenda-se timeout curto (falha rápido) + retry
  com backoff, herdados de BaseConnector.

ATENÇÃO: os demais endpoints de consulta (contratações por publicação, atas,
licitações) são citados no Manual de Integração v2.5, mas NÃO foram verificados
contra a API viva (ela estava instável). Verificar no Swagger antes de adicionar.
"""

from __future__ import annotations

from typing import Any, Optional

from connectors.base import BaseConnector
from interoperability import normalize_cnpj

PNCP_BASE_URL = "https://pncp.gov.br/api/consulta"

# CNPJ da Prefeitura de BH (usado como filtro padrão nas consultas de órgão).
PBH_CNPJ = "18715383000140"


class PncpConnector(BaseConnector):
    """Cliente da API de consulta do PNCP (leitura pública)."""

    def __init__(
        self,
        base_url: str = PNCP_BASE_URL,
        timeout: float = 20.0,
        max_retries: int = 3,
        backoff: float = 2.0,
        **kwargs: Any,
    ) -> None:
        # Timeout curto + backoff maior: o backend do PNCP responde com 504 após
        # ~70s quando sobrecarregado; falhar rápido evita ficar pendurado.
        super().__init__(
            timeout=timeout, max_retries=max_retries, backoff=backoff, **kwargs
        )
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, *, params: Optional[dict] = None) -> Any:
        return self._get_json(f"{self.base_url}/{path.lstrip('/')}", params=params)

    # ------------------------------------------------------------------
    # endpoints verificados
    # ------------------------------------------------------------------
    def orgaos(self, pagina: int = 1, tamanho_pagina: int = 100) -> Any:
        """Lista os órgãos/entidades cadastrados (paginado).

        Resposta (Manual v2.5) é um envelope paginado; a estrutura exata deve ser
        conferida no Swagger quando a API estiver disponível.
        """
        return self._get(
            "v1/orgaos", params={"pagina": pagina, "tamanhoPagina": tamanho_pagina}
        )

    def orgao(self, cnpj: str) -> Any:
        """Metadados de um órgão pelo CNPJ (14 dígitos)."""
        cnpj = normalize_cnpj(cnpj)
        return self._get(f"v1/orgaos/{cnpj}")
