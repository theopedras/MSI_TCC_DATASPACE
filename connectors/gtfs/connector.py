"""Conector GTFS (estático + tempo real) da BHTRANS.

Pontos levantados no teste empírico (docs/03-implementacao/01-teste-apis.md):
- GTFS estático: ZIP em S3 (mobilibus), atualizado semanalmente.
- GTFS-Realtime: 3 feeds protobuf (trip-updates, vehicle-positions, alerts)
  em realtime4.mobilibus.com com accesskey na URL. O mapeamento da Etapa 1
  marcava GTFS-RT como "ausente" — na verdade existe e é protobuf legítimo.

Trade-off "consulta vs cache" (princípio do dataspace): o RT muda a cada
~15-30s (polling direto é ok p/ demonstração); o estático muda semanalmente.
"""

from __future__ import annotations

import csv
import io
import zipfile
from typing import Any, Optional

from google.protobuf.json_format import MessageToDict
from google.transit import gtfs_realtime_pb2

from connectors.base import BaseConnector

GTFS_STATIC_URL = "https://s3.amazonaws.com/mobilibus-uploads/gtfs/GTFSBHTRANS.zip"

GTFS_RT_URLS = {
    "trip_updates": (
        "http://realtime4.mobilibus.com/web/4ch6j/trip-updates"
        "?accesskey=982a57efd77a9462bf1665696fb25984"
    ),
    "vehicle_positions": (
        "http://realtime4.mobilibus.com/web/4ch6j/vehicle-positions"
        "?accesskey=982a57efd77a9462bf1665696fb25984"
    ),
    "alerts": (
        "http://realtime4.mobilibus.com/web/4ch6j/alerts"
        "?accesskey=982a57efd77a9462bf1665696fb25984"
    ),
}

# Map (nome do recurso CKAN) -> (feed RT). Usado em from_ckan().
_RT_BY_RESOURCE_NAME = {
    "atualizações de viagem": "trip_updates",
    "posição de veículos": "vehicle_positions",
    "alertas de serviço": "alerts",
}


class GtfsConnector(BaseConnector):
    """Cliente GTFS estático + GTFS-Realtime (BHTRANS)."""

    def __init__(
        self,
        static_url: str = GTFS_STATIC_URL,
        rt_urls: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.static_url = static_url
        self.rt_urls = rt_urls or GTFS_RT_URLS

    # ------------------------------------------------------------------
    # estático
    # ------------------------------------------------------------------
    def download_static(self) -> bytes:
        """Baixa o ZIP do GTFS estático (bytes)."""
        resp = self._request(
            "GET", self.static_url, headers={"Accept": "application/zip, */*"}
        )
        return resp.content

    def static_feed(self) -> dict[str, list[dict]]:
        """Baixa e parseia o GTFS estático -> {tabela: [linha, ...]}.

        Chaves: agency, routes, trips, stops, stop_times, calendar, ... (uma por
        .txt dentro do ZIP). Cada linha é um dict com os campos do CSV.
        """
        data = self.download_static()
        zf = zipfile.ZipFile(io.BytesIO(data))
        tables: dict[str, list[dict]] = {}
        for name in zf.namelist():
            if not name.endswith(".txt"):
                continue
            key = name.rsplit("/", 1)[-1][:-4]  # remove caminho e ".txt"
            with zf.open(name) as f:
                text = io.TextIOWrapper(f, encoding="utf-8-sig")
                tables[key] = [dict(row) for row in csv.DictReader(text)]
        return tables

    # ------------------------------------------------------------------
    # tempo real (protobuf -> dict)
    # ------------------------------------------------------------------
    def _realtime_raw(self, kind: str) -> dict:
        """Baixa um feed RT e devolve o MessageToDict (estrutura completa)."""
        if kind not in self.rt_urls:
            raise ValueError(f"feed RT desconhecido: {kind}")
        resp = self._request(
            "GET",
            self.rt_urls[kind],
            headers={"Accept": "application/x-google-protobuf, */*"},
        )
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
        return MessageToDict(feed)

    def vehicle_positions(self) -> list[dict]:
        """Posição dos veículos em trânsito (lista achatada)."""
        raw = self._realtime_raw("vehicle_positions")
        out: list[dict] = []
        for entity in raw.get("entity", []):
            v = entity.get("vehicle", {})
            trip = v.get("trip", {})
            pos = v.get("position", {})
            vehicle = v.get("vehicle", {})
            out.append(
                {
                    "entity_id": entity.get("id"),
                    "trip_id": trip.get("tripId"),
                    "route_id": trip.get("routeId"),
                    "direction_id": trip.get("directionId"),
                    "start_time": trip.get("startTime"),
                    "start_date": trip.get("startDate"),
                    "latitude": pos.get("latitude"),
                    "longitude": pos.get("longitude"),
                    "bearing": pos.get("bearing"),
                    "speed": pos.get("speed"),
                    "current_status": v.get("currentStatus"),
                    "current_stop_sequence": v.get("currentStopSequence"),
                    "stop_id": v.get("stopId"),
                    "timestamp": v.get("timestamp"),
                    "vehicle_id": vehicle.get("id"),
                    "vehicle_label": vehicle.get("label"),
                }
            )
        return out

    def trip_updates(self) -> list[dict]:
        """Atualizações de viagem (atrasos, partidas/chegadas previstas)."""
        raw = self._realtime_raw("trip_updates")
        out: list[dict] = []
        for entity in raw.get("entity", []):
            tu = entity.get("tripUpdate", {})
            trip = tu.get("trip", {})
            out.append(
                {
                    "entity_id": entity.get("id"),
                    "trip_id": trip.get("tripId"),
                    "route_id": trip.get("routeId"),
                    "start_time": trip.get("startTime"),
                    "start_date": trip.get("startDate"),
                    "vehicle_id": tu.get("vehicle", {}).get("id"),
                    "stop_time_update": tu.get("stopTimeUpdate", []),
                }
            )
        return out

    def alerts(self) -> list[dict]:
        """Alertas de serviço (interrupções, desvios, etc.)."""
        raw = self._realtime_raw("alerts")
        out: list[dict] = []
        for entity in raw.get("entity", []):
            a = entity.get("alert", {})
            header = a.get("headerText", {})
            description = a.get("descriptionText", {})
            out.append(
                {
                    "entity_id": entity.get("id"),
                    "cause": a.get("cause"),
                    "effect": a.get("effect"),
                    "header": _first_translation(header),
                    "description": _first_translation(description),
                    "active_period": a.get("activePeriod", []),
                    "informed_entity": a.get("informedEntity", []),
                }
            )
        return out

    # ------------------------------------------------------------------
    # descoberta via catálogo CKAN
    # ------------------------------------------------------------------
    @classmethod
    def from_ckan(cls, ckan_connector: Any) -> "GtfsConnector":
        """Descobre as URLs dos feeds a partir dos datasets 'gtfs' e 'gtfs-rt' do CKAN."""
        gtfs_pkg = ckan_connector.package_show("gtfs")
        static_url = next(
            (r["url"] for r in gtfs_pkg["resources"] if str(r.get("url", "")).endswith(".zip")),
            GTFS_STATIC_URL,
        )
        rt_pkg = ckan_connector.package_show("gtfs-rt")
        rt_urls: dict[str, str] = {}
        for r in rt_pkg["resources"]:
            key = _RT_BY_RESOURCE_NAME.get((r.get("name") or "").lower())
            if key and r.get("url"):
                rt_urls[key] = r["url"]
        return cls(static_url=static_url, rt_urls=rt_urls or GTFS_RT_URLS)


def _first_translation(text: Optional[dict]) -> Optional[str]:
    """Extrai a primeira tradução de um TranslatedString do GTFS-RT."""
    if not text:
        return None
    translations = text.get("translation", [])
    return translations[0].get("text") if translations else None
