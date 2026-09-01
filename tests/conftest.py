"""Configuração dos testes.

Testes de integração (que batem nas APIs reais das fontes) são marcados com
@pytest.mark.integration e ficam SKIPADOS por padrão, para o `pytest` do dia a dia
ser rápido e não sobrecarregar os servidores públicos. Rode com:

    pytest --integration          # roda tudo, incluindo as APIs reais
    pytest                        # só os unitários (rápido, sem rede)
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="rodar também os testes de integração (batem nas APIs reais)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--integration"):
        return
    skip = pytest.mark.skip(reason="teste de integração (use --integration)")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
