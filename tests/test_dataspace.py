"""Testes do orquestrador Dataspace (conectores simulados)."""

from unittest.mock import Mock

from dataspace import Dataspace


def test_academias_por_100k_cruza_bhgeo_com_ibge():
    ds = Dataspace()
    ds.ogc.get_feature = Mock(return_value={"totalFeatures": 83})
    ds.ibge.dados_simples = Mock(
        return_value=[{"valor": "2530701", "localidade_id": "3106200"}]
    )

    result = ds.academias_por_100k(ano="2021")

    assert result["municipio"] == "3106200"
    assert result["populacao"] == 2530701
    assert result["academias"] == 83
    assert result["academias_por_100k"] == 3.28
    # confirma que o WFS foi chamado com reprojeção p/ WGS84
    assert ds.ogc.get_feature.call_args.kwargs["srs"] == "EPSG:4326"


def test_populacao_normaliza_codigo_e_converte_valor():
    ds = Dataspace()
    ds.ibge.dados_simples = Mock(return_value=[{"valor": "2.530.701"}])
    assert ds.populacao("3106200", "2021") == 2530701
    # código passado normalizado para o IBGE
    assert ds.ibge.dados_simples.call_args.args[3] == "3106200"


def test_harvest_ckan_respeita_limit():
    ds = Dataspace()
    ds.ckan.package_list = Mock(return_value=["a", "b", "c"])
    ds.ckan_harvester.harvest = Mock(side_effect=lambda x: x)
    # harvest retorna objetos mock; catalog.add aceita qualquer Dataset-like aqui
    ds.catalog.add = Mock()
    n = ds.harvest_ckan(limit=2)
    assert n == 2
    assert ds.ckan_harvester.harvest.call_count == 2
