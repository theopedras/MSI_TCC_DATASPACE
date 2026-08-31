# MSI TCC — Dataspace de Dados Abertos (Belo Horizonte)

Trabalho de Conclusão de Curso (MSI — POC I/MSI I → POC II/MSI II)
Departamento de Ciência da Computação — UFMG

- Autor: Theo Lopes Mesquita Pedras
- Orientadora: Patrícia Nascimento Silva
- Tipo de pesquisa: Tecnológica

## Pergunta de pesquisa

Como organizar dados e estruturar dataspaces com foco no acesso e reúso pela sociedade?

## Objetivo

Estruturar e implementar uma arquitetura para data spaces com foco na organização da
informação e em fontes de dados abertos, governamentais e não governamentais.

Princípio central: os dados permanecem nas fontes de origem e são integrados via
mecanismos interoperáveis (APIs, metadados, padrões de comunicação) — não por um
repositório central que copia tudo.

## Estado atual

- Etapa 1 (concluída): levantamento exploratório e inventário técnico de fontes de dados
  abertos de BH → docs/01-mapeamento/
- Próximas etapas: definição de arquitetura + modelo de metadados (DCAT), implementação
  dos conectores, catálogo, camada de interoperabilidade, testes e validação.

## Fontes selecionadas para o protótipo (5)

| # | Fonte | Tipo de conector |
|---|-------|------------------|
| 1 | CKAN da PBH (dados.pbh.gov.br) | CKAN genérico |
| 2 | BHGEO/BHMAP (WMS/WFS, OGC) | OGC + reprojeção SRID |
| 3 | GTFS / tempo-real BHTRANS | arquivo/polling |
| 4 | IBGE — API de Agregados (SIDRA) | REST |
| 5 | PNCP — API de Consultas | REST |

As 5 cobrem deliberadamente 4 arquiteturas técnicas distintas (CKAN, OGC/WMS-WFS,
download/polling, REST puro), o que força o protótipo a implementar mais de um tipo de
conector.

## Estrutura do repositório

    docs/
      projeto/            proposta formal (PDF) + resumo
      01-mapeamento/      inventário de fontes (Etapa 1)
      02-arquitetura/     arquitetura do dataspace + modelo de metadados DCAT
      03-implementacao/   resultados de teste/validação
    connectors/
      ckan/               conector CKAN genérico (PBH + MG)
      ogc/                conector WMS/WFS (BHGEO) + reprojeção EPSG:31983→4326
      rest/               conectores REST (IBGE + PNCP)
    catalog/              catálogo de metadados DCAT
    interoperability/     normalização de chaves (código IBGE 3106200, CNPJ)
    tests/                testes de integração com as fontes

## Problemas de interoperabilidade identificados

- SRID divergente: BHGEO usa EPSG:31983 (SIRGAS 2000 / UTM 23S); fontes nacionais usam
  EPSG:4326 (WGS84) → exige camada de reprojeção.
- Ausência de GTFS-Realtime: posição de ônibus em formato próprio, não GTFS-RT.
- Falta de identificador único compartilhado (obra/escola) entre secretarias.
- Fontes sem API REST (TabNet/DATASUS) exigem ETL, fora do princípio "dado na fonte".
- Rate limit não documentado em várias APIs municipais.

## Stack

Python: curl_cffi (HTTP com impersonação de navegador — WAF gocache da PBH),
pyproj (reprojeção), gtfs-realtime-bindings (protobuf), pydantic.

## Cronograma (13 semanas, entrega 01/12/2026)

| Semana | Atividade |
|--------|-----------|
| 1–2 | Revisão de literatura (data spaces, IDSA, Gaia-X) + mapeamento de dataspaces em operação |
| 3 | Mapeamento das fontes de BH |
| 4 | Definição da arquitetura e modelo de metadados (DCAT) |
| 5 | Conector CKAN genérico |
| 6 | Conector OGC (WMS/WFS) + reprojeção |
| 7 | Conector REST (IBGE, PNCP) + normalização de identificadores |
| 8 | Catálogo de metadados (DCAT) |
| 9 | Camada de interoperabilidade e integração |
| 10 | Testes de integração |
| 11 | Validação da interoperabilidade |
| 12–13 | Documentação técnica + relatório final |
