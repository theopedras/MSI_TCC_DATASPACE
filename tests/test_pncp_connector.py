"""Testes do PncpConnector (sem rede)."""

from unittest.mock import Mock

import pytest

from connectors.base import ServerError
from connectors.rest import PBH_CNPJ, PncpConnector


def test_timeout_curto_e_backoff_maior_por_padrao():
    c = PncpConnector()
    assert c.timeout == 20.0
    assert c.backoff == 2.0
    assert c.max_retries == 3


def test_orgaos_monta_url_e_paginacao():
    c = PncpConnector()
    captured = {}
    c._get_json = Mock(side_effect=lambda url, params: captured.update(url=url, params=params) or [])
    c.orgaos(pagina=2, tamanho_pagina=50)
    assert captured["url"] == "https://pncp.gov.br/api/consulta/v1/orgaos"
    assert captured["params"] == {"pagina": 2, "tamanhoPagina": 50}


def test_orgao_normaliza_cnpj():
    c = PncpConnector()
    captured = {}
    c._get_json = Mock(side_effect=lambda url, params: captured.update(url=url) or {})
    c.orgao("18.715.383/0001-40")
    assert captured["url"] == "https://pncp.gov.br/api/consulta/v1/orgaos/18715383000140"


def test_orgao_cnpj_invalido_levanta():
    c = PncpConnector()
    with pytest.raises(ValueError):
        c.orgao("123")


def test_retry_em_504(monkeypatch):
    c = PncpConnector(backoff=0)
    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            m = Mock()
            m.status_code = 504
            m.text = ""
            return m
        m = Mock()
        m.status_code = 200
        m.text = ""
        m.json.return_value = {}
        return m

    monkeypatch.setattr(c.session, "request", fake_request)
    resp = c._request("GET", "https://x/v1/orgaos")
    assert resp.status_code == 200
    assert calls["n"] == 2


def test_pbh_cnpj_constante():
    assert PBH_CNPJ == "18715383000140"
