"""Conector genérico para catálogos CKAN (Action API v3).

Reutilizável para a PBH (dados.pbh.gov.br) e para o Portal de MG
(dados.mg.gov.br), bastando instanciar com outra base_url — ambos usam a
mesma Action API e estrutura de metadados.

Pontos levantados no teste empírico (docs/03-implementacao/01-teste-apis.md):
- User-Agent de navegador é obrigatório (herdado de BaseConnector).
- datastore_search funciona; datastore_search_sql é 403 (SQL desabilitado).
- Datasets acumulam um recurso por snapshot mensal -> latest_resource().
"""

from __future__ import annotations

import re
from typing import Any, Optional

from connectors.base import BaseConnector, ConnectorError

PBH_BASE_URL = "https://dados.pbh.gov.br/api/3/action"
MG_BASE_URL = "https://dados.mg.gov.br/api/3/action"

_DATE_IN_NAME = re.compile(r"(20\d{2})(0[1-9]|1[0-2])([0-3]\d)")


def _is_dictionary_resource(resource: dict) -> bool:
    """Heurística: identifica 'Dicionário de dados' (PDF/HTML), não é dado."""
    name = (resource.get("name") or "").lower()
    fmt = (resource.get("format") or "").lower()
    if "dicion" in name or "dicion" in (resource.get("description") or "").lower():
        return True
    if fmt in ("pdf", "html", "docx", "url") and "dicion" in name:
        return True
    return False


class CkanConnector(BaseConnector):
    """Cliente da CKAN Action API (leitura)."""

    def __init__(
        self,
        base_url: str = PBH_BASE_URL,
        user_agent: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if user_agent is None:
            super().__init__(**kwargs)
        else:
            super().__init__(user_agent=user_agent, **kwargs)
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # infra
    # ------------------------------------------------------------------
    def _action(self, name: str, **params: Any) -> Any:
        """Chama /api/3/action/<name> e desembrulha o envelope {'success','result'}."""
        url = f"{self.base_url}/{name}"
        data = self._get_json(url, params=params or None)
        if not isinstance(data, dict) or not data.get("success"):
            error = data.get("error") if isinstance(data, dict) else data
            raise ConnectorError(f"CKAN action '{name}' falhou: {error}")
        return data.get("result")

    # ------------------------------------------------------------------
    # descoberta
    # ------------------------------------------------------------------
    def package_list(self) -> list[str]:
        """Lista os identificadores (name) de todos os datasets."""
        return self._action("package_list")

    def organizations(self) -> list[dict]:
        """Organizações com contagem de datasets (all_fields=true)."""
        return self._action("organization_list", all_fields="true")

    def groups(self) -> list[dict]:
        """Grupos temáticos com contagem de datasets."""
        return self._action("group_list", all_fields="true")

    def tags(self) -> list[dict]:
        """Tags do catálogo."""
        return self._action("tag_list", all_fields="true")

    # ------------------------------------------------------------------
    # busca e detalhe
    # ------------------------------------------------------------------
    def search(
        self,
        q: Optional[str] = None,
        fq: Optional[str] = None,
        rows: int = 100,
        start: int = 0,
    ) -> dict:
        """package_search: retorna {'count': int, 'results': [...]}.

        Suporta paginação (rows/start) e filtros (fq, ex. 'organization:bhtrans').
        """
        params: dict[str, Any] = {"rows": rows, "start": start}
        if q:
            params["q"] = q
        if fq:
            params["fq"] = fq
        return self._action("package_search", **params)

    def search_all(self, q: Optional[str] = None, fq: Optional[str] = None) -> list[dict]:
        """Varre todas as páginas de package_search e devolve todos os resultados."""
        results: list[dict] = []
        start = 0
        while True:
            page = self.search(q=q, fq=fq, rows=100, start=start)
            results.extend(page["results"])
            start += len(page["results"])
            if start >= page["count"] or not page["results"]:
                break
        return results

    def package_show(self, dataset_id: str) -> dict:
        """Metadados completos de um dataset (recursos, tags, licença, extras)."""
        return self._action("package_show", id=dataset_id)

    # ------------------------------------------------------------------
    # dados tabulares (Datastore)
    # ------------------------------------------------------------------
    def datastore_search(
        self,
        resource_id: str,
        limit: int = 100,
        offset: int = 0,
        q: Optional[str] = None,
        filters: Optional[dict] = None,
        fields: Optional[list[str]] = None,
    ) -> dict:
        """Consulta tabular in-place via Datastore (retorna {'total', 'records', 'fields'}).

        NOTA: datastore_search_sql (SQL bruto) é 403 neste portal; use filtros.
        """
        params: dict[str, Any] = {"resource_id": resource_id, "limit": limit, "offset": offset}
        if q:
            params["q"] = q
        if filters:
            params["filters"] = filters
        if fields:
            params["fields"] = ",".join(fields)
        return self._action("datastore_search", **params)

    # ------------------------------------------------------------------
    # seleção de snapshot mais recente
    # ------------------------------------------------------------------
    @staticmethod
    def _resource_date(resource: dict) -> Optional[str]:
        """Extrai a data do recurso: YYYYMMDD no nome, senão last_modified/created."""
        m = _DATE_IN_NAME.search(resource.get("name") or "")
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        for key in ("last_modified", "created", "metadata_modified"):
            v = resource.get(key)
            if v:
                return v[:10]
        return None

    def latest_resource(
        self,
        dataset: Any,
        format: Optional[str] = None,
    ) -> Optional[dict]:
        """Devolve o recurso de dados mais recente de um dataset.

        O CKAN da PBH acumula um recurso por snapshot mensal (sem um 'latest'
        explícito). A heurística ignora dicionários e escolhe o de maior data.

        dataset pode ser um id (str) ou o dict de package_show.
        """
        if isinstance(dataset, str):
            pkg = self.package_show(dataset)
        else:
            pkg = dataset
        resources = pkg.get("resources", [])
        candidates = [
            r
            for r in resources
            if not _is_dictionary_resource(r)
            and (format is None or (r.get("format") or "").lower() == format.lower())
        ]
        if not candidates:
            candidates = [r for r in resources if not _is_dictionary_resource(r)]
        if not candidates:
            return None

        def sort_key(r: dict) -> tuple:
            # data desc; desempata por posição
            return (self._resource_date(r) or "", -int(r.get("position", 0)))

        return max(candidates, key=sort_key)
