"""Testes do IbgeConnector (sem rede)."""

from unittest.mock import Mock

from connectors.rest import BH_IBGE_CODE, IbgeConnector


def test_dados_junta_listas_com_virgula():
    c = IbgeConnector()
    c._get = Mock(return_value=[])
    c.dados("6579", periodos=["2021", "2022"], variaveis=["9324"], localidades="3106200")
    path = c._get.call_args[0][0]
    assert path == "/api/v3/agregados/6579/periodos/2021,2022/variaveis/9324"
    assert c._get.call_args.kwargs["params"] == {"localidades": "3106200"}


def test_dados_simples_achata_resposta_aninhada():
    c = IbgeConnector()
    c.dados = Mock(
        return_value=[
            {
                "id": "9324",
                "variavel": "População residente estimada",
                "unidade": "Pessoas",
                "resultados": [
                    {
                        "classificacoes": [],
                        "series": [
                            {
                                "localidade": {"id": "3106200", "nome": "Belo Horizonte (MG)"},
                                "serie": {"2021": "2530701", "2022": "2540000"},
                            }
                        ],
                    }
                ],
            }
        ]
    )
    flat = c.dados_simples("6579", "2021,2022", "9324", "3106200")
    assert len(flat) == 2
    assert flat[0] == {
        "variavel_id": "9324",
        "variavel": "População residente estimada",
        "unidade": "Pessoas",
        "localidade_id": "3106200",
        "localidade": "Belo Horizonte (MG)",
        "periodo": "2021",
        "valor": "2530701",
    }


def test_malha_usa_formato_geojson_e_codigo_padrao_bh():
    c = IbgeConnector()
    c._get = Mock(return_value={"type": "FeatureCollection"})
    c.malha()
    path = c._get.call_args[0][0]
    assert path == f"/api/v2/malhas/{BH_IBGE_CODE}"
    assert c._get.call_args.kwargs["params"] == {"formato": "application/vnd.geo+json"}


def test_localidades_monta_filtros():
    c = IbgeConnector()
    c._get = Mock(return_value=[])
    c.localidades("municipios", UF="MG")
    assert c._get.call_args[0][0] == "/api/v1/localidades/municipios"
    assert c._get.call_args.kwargs["params"] == {"UF": "MG"}
