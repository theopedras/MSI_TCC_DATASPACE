"""Conector REST para o IBGE (API de Agregados/SIDRA e Malhas).

Fluxo documentado (docs/03-implementacao/01-teste-apis.md):
  /api/v3/agregados  -> pesquisas (Censo Demográfico, Estimativas de População, ...)
  /api/v3/agregados/{id}/metadados -> variáveis
  /api/v3/agregados/{id}/periodos  -> períodos
  /api/v3/agregados/{id}/periodos/{p}/variaveis/{v}?localidades={l} -> dados
  /api/v2/malhas/{municipio}?formato=application/vnd.geo+json -> geometria (EPSG:4326)

BH = código IBGE 3106200.
"""

from __future__ import annotations

from typing import Any, Optional

from connectors.base import BaseConnector

IBGE_BASE_URL = "https://servicodados.ibge.gov.br"

BH_IBGE_CODE = "3106200"


class IbgeConnector(BaseConnector):
    """Cliente da API do IBGE (leitura)."""

    def __init__(self, base_url: str = IBGE_BASE_URL, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, *, params: Optional[dict] = None) -> Any:
        return self._get_json(f"{self.base_url}/{path.lstrip('/')}", params=params)

    # ------------------------------------------------------------------
    # agregados (SIDRA)
    # ------------------------------------------------------------------
    def agregados(self) -> list[dict]:
        """Lista as pesquisas (agrupamentos de agregados SIDRA)."""
        return self._get("/api/v3/agregados")

    def agregado_metadados(self, agregado: str) -> dict:
        """Metadados de um agregado: nome, variáveis, classificações."""
        return self._get(f"/api/v3/agregados/{agregado}/metadados")

    def agregado_periodos(self, agregado: str) -> list[dict]:
        """Períodos disponíveis de um agregado."""
        return self._get(f"/api/v3/agregados/{agregado}/periodos")

    def dados(
        self,
        agregado: str,
        periodos: Any,
        variaveis: Any,
        localidades: Any,
    ) -> list[dict]:
        """Busca os dados efetivos de um agregado.

        periodos/variaveis/localidades aceitam str ('2021') ou lista (['2021','2022']);
        listas são convertidas em valores separados por vírgula (padrão da API).
        """
        def _join(x: Any) -> str:
            return x if isinstance(x, str) else ",".join(str(i) for i in x)

        path = (
            f"/api/v3/agregados/{agregado}/periodos/{_join(periodos)}"
            f"/variaveis/{_join(variaveis)}"
        )
        return self._get(path, params={"localidades": _join(localidades)})

    def dados_simples(
        self,
        agregado: str,
        periodos: Any,
        variaveis: Any,
        localidades: Any,
    ) -> list[dict]:
        """Igual a dados(), mas achata a resposta aninhada do IBGE.

        Devolve uma lista de registros planos:
          {variavel_id, variavel, unidade, localidade_id, localidade, periodo, valor}
        """
        raw = self.dados(agregado, periodos, variaveis, localidades)
        flat: list[dict] = []
        for item in raw:
            var_id = item["id"]
            var_nome = item.get("variavel")
            unidade = item.get("unidade")
            for resultado in item.get("resultados", []):
                for serie in resultado.get("series", []):
                    loc = serie["localidade"]
                    for periodo, valor in serie["serie"].items():
                        flat.append(
                            {
                                "variavel_id": var_id,
                                "variavel": var_nome,
                                "unidade": unidade,
                                "localidade_id": loc["id"],
                                "localidade": loc["nome"],
                                "periodo": periodo,
                                "valor": valor,
                            }
                        )
        return flat

    # ------------------------------------------------------------------
    # malhas (geometria)
    # ------------------------------------------------------------------
    def malha(self, municipio: str = BH_IBGE_CODE) -> dict:
        """Malha geográfica (contorno) de um município em GeoJSON (EPSG:4326)."""
        return self._get(
            f"/api/v2/malhas/{municipio}",
            params={"formato": "application/vnd.geo+json"},
        )

    # ------------------------------------------------------------------
    # localidades
    # ------------------------------------------------------------------
    def localidades(self, nivel: str = "municipios", **filtros: Any) -> list[dict]:
        """Lista localidades (estados, municípios, ...) com filtros opcionais.

        Ex.: localidades('municipios', UF='MG') -> municípios de MG.
        """
        return self._get(f"/api/v1/localidades/{nivel}", params=filtros or None)
