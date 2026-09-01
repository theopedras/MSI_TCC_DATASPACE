"""Testes do GtfsConnector (sem rede)."""

import io
import zipfile
from unittest.mock import Mock

from connectors.gtfs import GtfsConnector, GTFS_RT_URLS
from connectors.gtfs.connector import _first_translation


def _gtfs_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("routes.txt", "route_id,route_short_name\n1,A\n2,B\n")
        zf.writestr("stops.txt", "stop_id,stop_name\ns1,Centro\n")
    return buf.getvalue()


def test_static_feed_parseia_zip_em_tabelas():
    c = GtfsConnector()
    c.download_static = Mock(return_value=_gtfs_zip())
    tables = c.static_feed()
    assert set(tables.keys()) == {"routes", "stops"}
    assert tables["routes"] == [
        {"route_id": "1", "route_short_name": "A"},
        {"route_id": "2", "route_short_name": "B"},
    ]
    assert tables["stops"][0]["stop_name"] == "Centro"


def test_vehicle_positions_achata_entity():
    c = GtfsConnector()
    c._realtime_raw = Mock(
        return_value={
            "entity": [
                {
                    "id": "21303",
                    "vehicle": {
                        "trip": {"tripId": "8551 011080022100", "routeId": "8551", "directionId": 0},
                        "position": {"latitude": -19.86, "longitude": -43.95, "bearing": 328.0},
                        "currentStatus": "IN_TRANSIT_TO",
                        "timestamp": "1788221608",
                        "vehicle": {"id": "21303", "label": "Estação São Gabriel"},
                    },
                }
            ]
        }
    )
    out = c.vehicle_positions()
    assert len(out) == 1
    r = out[0]
    assert r["route_id"] == "8551"
    assert r["latitude"] == -19.86
    assert r["vehicle_id"] == "21303"


def test_alerts_extrai_texto_e_campos():
    c = GtfsConnector()
    c._realtime_raw = Mock(
        return_value={
            "entity": [
                {
                    "id": "1",
                    "alert": {
                        "cause": "ACCIDENT",
                        "effect": "DETOUR",
                        "headerText": {"translation": [{"text": "Desvio na linha X"}]},
                        "descriptionText": {"translation": [{"text": "Obras na av. Y"}]},
                    },
                }
            ]
        }
    )
    out = c.alerts()
    assert out[0]["cause"] == "ACCIDENT"
    assert out[0]["header"] == "Desvio na linha X"
    assert out[0]["description"] == "Obras na av. Y"


def test_first_translation_vazio():
    assert _first_translation(None) is None
    assert _first_translation({"translation": []}) is None


def test_rt_urls_padrao():
    c = GtfsConnector()
    assert set(c.rt_urls) == {"trip_updates", "vehicle_positions", "alerts"}
    assert c.rt_urls == GTFS_RT_URLS


def test_from_ckan_descobre_urls():
    ckan = Mock()
    ckan.package_show = Mock(
        side_effect=lambda name: {
            "gtfs": {
                "resources": [
                    {"url": "https://x/gtfs.zip", "name": "GTFS"},
                ]
            },
            "gtfs-rt": {
                "resources": [
                    {"url": "http://rt/vehicle-positions?k=1", "name": "Posição de veículos"},
                    {"url": "http://rt/trip-updates?k=1", "name": "Atualizações de viagem"},
                    {"url": "http://rt/alerts?k=1", "name": "Alertas de serviço"},
                ]
            },
        }[name]
    )
    c = GtfsConnector.from_ckan(ckan)
    assert c.static_url == "https://x/gtfs.zip"
    assert c.rt_urls["vehicle_positions"] == "http://rt/vehicle-positions?k=1"
    assert c.rt_urls["alerts"] == "http://rt/alerts?k=1"
