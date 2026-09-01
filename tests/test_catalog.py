"""Testes do catálogo DCAT (modelo + harvester + registro)."""

from catalog import Catalog, CkanHarvester, Dataset
from catalog.models import Distribution, Publisher


def _fake_package():
    return {
        "id": "abc-123",
        "name": "sinalizacao-semaforica",
        "title": "Sinalização Semafórica",
        "notes": "Sinalização semafórica de BH",
        "organization": {"name": "bhtrans", "title": "BHTRANS"},
        "license_title": "Creative Commons Attribution",
        "license_id": "cc-by",
        "tags": [{"name": "sinalização"}, {"name": "transporte"}],
        "resources": [
            {
                "name": "20260803_sinalizacao_semaforica",
                "format": "CSV",
                "url": "https://ckan.pbh.gov.br/...",
                "last_modified": "2026-08-03T00:00:00",
            }
        ],
        "metadata_created": "2022-05-12T16:54:13",
        "metadata_modified": "2026-08-15T03:10:55",
    }


def test_from_ckan_mapeia_campos_dcat():
    ds = Dataset.from_ckan(_fake_package())
    assert ds.identifier == "abc-123"
    assert ds.title == "Sinalização Semafórica"
    assert ds.license == "Creative Commons Attribution"
    assert ds.keywords == ["sinalização", "transporte"]
    assert isinstance(ds.publisher, Publisher)
    assert ds.publisher.name == "BHTRANS"
    assert len(ds.distributions) == 1
    assert isinstance(ds.distributions[0], Distribution)
    assert ds.distributions[0].format == "CSV"


def test_harvester_usa_connector():
    class FakeConnector:
        base_url = "https://x/api/3/action"

        def package_show(self, dataset_id):
            assert dataset_id == "abc"
            return _fake_package()

        def package_list(self):
            return ["abc"]

    h = CkanHarvester(FakeConnector())
    ds = h.harvest("abc")
    assert ds.title == "Sinalização Semafórica"
    assert ds.source == "https://x/api/3/action"


def test_catalog_add_get_search():
    c = Catalog()
    ds1 = Dataset.from_ckan(_fake_package())
    ds2 = _fake_package()
    ds2["id"] = "xyz"
    ds2["title"] = "Redutor de Velocidade"
    ds2["notes"] = "Dispositivos de redução de velocidade"
    ds2["tags"] = [{"name": "trânsito"}]
    c.add(ds1)
    c.add(Dataset.from_ckan(ds2))

    assert len(c) == 2
    got = c.get("xyz")
    assert got is not None and got.title == "Redutor de Velocidade"
    assert [d.identifier for d in c.search("semafórica")] == ["abc-123"]
