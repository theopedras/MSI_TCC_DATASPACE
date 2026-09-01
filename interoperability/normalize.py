"""Normalizações da camada de interoperabilidade.

Funções puras que tratam os problemas concretos de interoperabilidade
levantados no mapeamento (docs/03-implementacao/01-teste-apis.md):
  - chave de junção: código IBGE do município (7 dígitos)
  - valores numéricos em string (IBGE devolve "2530701", fontes BR usam "1.234,56")
  - taxas por 100 mil habitantes (comparabilidade entre municípios)
"""

from __future__ import annotations

from typing import Any, Union


def normalize_ibge_code(code: Union[str, int]) -> str:
    """Normaliza um código de município IBGE para 7 dígitos (ex. '3106200').

    Remove máscaras (pontos, hífens, espaços) e valida o tamanho.
    """
    digits = "".join(ch for ch in str(code) if ch.isdigit())
    if len(digits) != 7:
        raise ValueError(
            f"código IBGE inválido: '{code}' -> '{digits}' (esperado 7 dígitos)"
        )
    return digits


def to_float(value: Any) -> float:
    """Converte valor numérico (str/int/float) para float, tratando formato BR.

    Convenções assumidas (padrão brasileiro):
      - vírgula é separador decimal; ponto é separador de milhar.
        '1.234,56' -> 1234.56 ; '2.530.701' -> 2530701.0 ; '2530701' -> 2530701.0
    """
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        raise ValueError("valor numérico vazio")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    return float(s)


def per_100k(numerador: float, denominador: float) -> float:
    """Taxa por 100 mil habitantes (numerador / denominador * 100000)."""
    if denominador == 0:
        raise ZeroDivisionError("denominador (população) é zero")
    return float(numerador) / float(denominador) * 100000.0
