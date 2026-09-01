"""Modelo de metadados inspirado no DCAT (W3C).

Campos principais do vocabulário DCAT mapeados para o contexto do dataspace:
  dcat:Dataset      -> Dataset
  dcat:Distribution -> Distribution
  dcat:Publisher    -> Publisher (foaf:Agent / dcat:Organization)

Cada modelo tem um método from_ckan() que converte o package_show da Action API
do CKAN (estrutura já próxima de DCAT) para o modelo canônico do dataspace.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Publisher(BaseModel):
    name: str
    identifier: Optional[str] = None


class Distribution(BaseModel):
    name: str
    format: Optional[str] = None
    access_url: Optional[str] = None
    modified: Optional[datetime] = None


class Dataset(BaseModel):
    identifier: str
    title: str
    description: Optional[str] = None
    publisher: Optional[Publisher] = None
    license: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    distributions: List[Distribution] = Field(default_factory=list)
    issued: Optional[datetime] = None
    modified: Optional[datetime] = None
    source: Optional[str] = None

    @classmethod
    def from_ckan(cls, package: dict[str, Any], source: Optional[str] = None) -> "Dataset":
        """Converte um package_show do CKAN em Dataset DCAT-like."""
        org = package.get("organization") or {}
        return cls(
            identifier=package.get("id") or package.get("name") or "",
            title=package.get("title") or package.get("name") or "",
            description=package.get("notes") or None,
            publisher=(
                Publisher(
                    name=org.get("title") or org.get("name") or "",
                    identifier=org.get("name"),
                )
                if org
                else None
            ),
            license=package.get("license_title") or package.get("license_id"),
            keywords=[t.get("name", "") for t in package.get("tags", []) if t.get("name")],
            distributions=[
                Distribution(
                    name=r.get("name") or "",
                    format=r.get("format") or None,
                    access_url=r.get("url") or None,
                    modified=r.get("last_modified") or None,
                )
                for r in package.get("resources", [])
            ],
            issued=package.get("metadata_created") or None,
            modified=package.get("metadata_modified") or None,
            source=source,
        )
