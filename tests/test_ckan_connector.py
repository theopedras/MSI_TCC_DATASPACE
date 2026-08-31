"""Testes do CkanConnector (sem rede — HTTP simulado)."""

from unittest.mock import Mock

import pytest

from connectors.base import (
    DEFAULT_USER_AGENT,
    AuthenticationError,
    ConnectorError,
    NotFoundError,
)
from connectors.ckan import CkanConnector, PBH_BASE_URL


def _resp(status_code=200, json_data=None, text=""):
    m = Mock()
    m.status_code = status_code
    m.text = text
    m.json.return_value = json_data if json_data is not None else {}
    return m


def _resource(name, created="2022-01-01T00:00:00", last_modified=None, fmt="CSV", position=0):
    return {
        "name": name,
        "format": fmt,
        "created": created,
        "last_modified": last_modified,
        "position": position,
    }


# ---------------------------------------------------------------------------
# User-Agent
# ---------------------------------------------------------------------------
def test_user_agent_eh_setado_por_padrao():
    c = CkanConnector()
    assert c.session.headers["User-Agent"] == DEFAULT_USER_AGENT
    assert c.session.headers["Accept"] == "application/json"


def test_base_url_default_pbh():
    assert CkanConnector().base_url == PBH_BASE_URL.rstrip("/")


# ---------------------------------------------------------------------------
# envelope CKAN
# ---------------------------------------------------------------------------
def test_action_desembrulha_result():
    c = CkanConnector()
    c._get_json = Mock(return_value={"success": True, "result": ["a", "b"]})
    assert c.package_list() == ["a", "b"]
    c._get_json.assert_called_once()
    url = c._get_json.call_args[0][0]
    assert url.endswith("/package_list")


def test_action_levanta_quando_success_false():
    c = CkanConnector()
    c._get_json = Mock(return_value={"success": False, "error": {"message": "x"}})
    with pytest.raises(ConnectorError):
        c.package_list()


# ---------------------------------------------------------------------------
# erros HTTP
# ---------------------------------------------------------------------------
def test_403_vira_authentication_error():
    c = CkanConnector()
    c.session.request = Mock(return_value=_resp(403, text="Acesso Bloqueado"))
    with pytest.raises(AuthenticationError):
        c._request("GET", "http://x")


def test_404_vira_not_found():
    c = CkanConnector()
    c.session.request = Mock(return_value=_resp(404))
    with pytest.raises(NotFoundError):
        c._request("GET", "http://x")


def test_retry_em_503_depois_sucesso(monkeypatch):
    c = CkanConnector(backoff=0)
    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _resp(503)
        return _resp(200, json_data={"ok": True})

    c.session.request = fake_request
    resp = c._request("GET", "http://x")
    assert resp.status_code == 200
    assert calls["n"] == 2


# ---------------------------------------------------------------------------
# busca / paginação
# ---------------------------------------------------------------------------
def test_search_monta_params_de_paginacao_e_filtro():
    c = CkanConnector()
    captured = {}
    c._action = Mock(side_effect=lambda name, **p: captured.update(p) or {"count": 0, "results": []})
    c.search(q="gtfs", fq="organization:bhtrans", rows=50, start=100)
    assert captured == {"rows": 50, "start": 100, "q": "gtfs", "fq": "organization:bhtrans"}


def test_search_all_varre_todas_as_paginas():
    c = CkanConnector()
    pages = [
        {"count": 3, "results": ["a", "b"]},
        {"count": 3, "results": ["c"]},
    ]
    c.search = Mock(side_effect=pages)
    assert c.search_all() == ["a", "b", "c"]
    assert c.search.call_count == 2


# ---------------------------------------------------------------------------
# latest_resource (snapshot mensal)
# ---------------------------------------------------------------------------
def test_latest_resource_escolhe_snapshot_mais_recente_pelo_nome():
    c = CkanConnector()
    pkg = {
        "resources": [
            _resource("20220601_sinalizacao_semaforica", position=1),
            _resource("20260803_sinalizacao_semaforica", position=2),
            _resource("20240502_sinalizacao_semaforica", position=3),
        ]
    }
    latest = c.latest_resource(pkg)
    assert latest["name"].startswith("20260803")


def test_latest_resource_ignora_dicionario_de_dados():
    c = CkanConnector()
    pkg = {
        "resources": [
            _resource("Dicionário de Dados", fmt="PDF", position=0),
            _resource("20260803_sinalizacao_semaforica", fmt="CSV", position=1),
        ]
    }
    latest = c.latest_resource(pkg)
    assert latest["name"].startswith("20260803")


def test_latest_resource_filtra_por_formato():
    c = CkanConnector()
    pkg = {
        "resources": [
            _resource("20260803_sinalizacao_semaforica", fmt="CSV", position=1),
            _resource("20260901_sinalizacao_semaforica", fmt="GeoJSON", position=2),
        ]
    }
    latest = c.latest_resource(pkg, format="GeoJSON")
    assert latest["format"] == "GeoJSON"
