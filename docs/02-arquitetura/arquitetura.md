# Arquitetura do Dataspace de Dados Abertos (BH)

Esboço da arquitetura, fundamentado nos resultados empíricos de
docs/03-implementacao/01-teste-apis.md. Documento vivo — evolui com a implementação.

## 1. Princípios de design

1. Dado permanece na fonte. O dataspace consulta as APIs das fontes sob demanda; não
   replica dados em repositório central. Exceções justificáveis (fora do escopo inicial):
   fontes sem API (TabNet) e cache local de curto prazo para dados de altíssima frequência.
2. Interoperabilidade por padrões abertos: CKAN Action API, OGC WMS/WFS, DCAT (W3C),
   GTFS/GTFS-Realtime.
3. Conectores reutilizáveis por tipo de arquitetura, não por fonte (um conector CKAN
   serve PBH e MG; um conector REST serve IBGE e PNCP).
4. Chave de junção universal: código IBGE do município (3106200 = BH). Chave secundária:
   CNPJ do órgão/empresa (PNCP).

## 2. Visão geral

    +----------------+     +-------------------+     +--------------------+     +-------------+
    |  Fonte (API)   | --> |  Conector         | --> |  Catálogo DCAT     | --> | Interoper.  |
    |                |     |  (por arquitetura)|     |  (metadados)       | --> | (normaliza) |
    +----------------+     +-------------------+     +--------------------+     +-------------+
                                                                                     |
                                                                                     v
    CKAN PBH/MG  ──> CKANConnector  ─┐                                        +-------------+
    BHGEO (OGC)  ──> OGCConnector   ─┼─> Dataspace core ──> normalização:     | Consumidor  |
    IBGE         ──> RESTConnector  ─┤                       - SRID -> 4326   | app/consulta|
    PNCP         ──> RESTConnector  ─┤                       - código IBGE    +-------------+
    GTFS/GTFS-RT ──> GtfsConnector ─┘                       - fuso (UTC-3)

## 3. Componentes

### 3.1 Conectores

Interface comum: cada conector expõe discovery() (o que a fonte oferece) e fetch()
(obter dado), normalizando a resposta para um formato interno (dicts/DataFrame).

#### CKANConnector (PBH e MG — mesma implementação, instâncias distintas)
- Base URL: https://dados.pbh.gov.br/api/3/action/ (espelho ckan.pbh.gov.br)
- OBRIGATÓRIO: curl_cffi com impersonação de navegador (o WAF gocache bloqueia por
  fingerprint TLS, não só por User-Agent — requests/urllib3 recebe 403)
- discovery(): organization_list, group_list, package_list, tag_list
- search(): package_search (q, fq, rows/start) — paginação nativa
- detail(): package_show (metadados do dataset)
- query(): datastore_search (consulta tabular in-place, sem baixar CSV; SQL via
  datastore_search_sql está BLOQUEADO -> usar filtros de campo)
- snapshot(): selecionar recurso mais recente (padrão de snapshot mensal: ordenar por
  created/last_modified/parse do nome YYYYMMDD)

#### OGCConnector (BHGEO/BHMAP — WMS/WFS)
- GetCapabilities (WMS + WFS) para discovery de camadas/feature types
- GetFeature com outputFormat=application/json (GeoJSON)
- Reprojeção server-side: srsName=urn:ogc:def:crs:EPSG::4326 (dispensa pyproj no happy path)
- pyproj como fallback para casos que exijam reprojeção local (ex.: GTFS com malha própria)

#### RESTConnector (IBGE, PNCP)
- IBGE: fluxo agregados -> metadados -> periodos -> variaveis -> dados (localidades=3106200);
  malhas em /api/v2/malhas/{municipio} (GeoJSON, EPSG:4326)
- PNCP: /api/consulta/v1/ (consulta pública), filtro por CNPJ do órgão; REQUER
  timeout agressivo + retry/backoff (backend instável — ver testes)

#### GtfsConnector (BHTRANS)
- GTFS estático: ZIP em S3 (mobilibus), atualização semanal — download + parse
- GTFS-Realtime: 3 feeds protobuf (trip-updates, vehicle-positions, alerts) em
  realtime4.mobilibus.com com accesskey — decode com gtfs-realtime-bindings

### 3.2 Catálogo de metadados (DCAT)

- Modelo inspirado no DCAT (W3C): Dataset, Distribution, Publisher, License, temporal,
  spatial, conformsTo (padrão/API).
- Alimentação: harvester do CKAN (package_show já fornece a maioria dos campos DCAT);
  fichas manuais para fontes fora do CKAN (BHGEO camadas, IBGE agregados, PNCP).
- Cada ficha registra: órgão, endpoint, autenticação, formato, protocolo, periodicidade,
  licença, identificadores (código IBGE / CNPJ), SRID e taxa de atualização esperada.

### 3.3 Camada de interoperabilidade

Normalizações no core do dataspace:
- SRID: tudo em EPSG:4326 na saída (BHGEO reprojeta server-side; IBGE já é 4326)
- Identificadores: código IBGE do município como chave universal; CNPJ para compras
- Fuso/timestamp: normalizar para America/Sao_Paulo (UTC-3), mantendo UTC na origem
- Formato de saída único: GeoJSON (espacial) / JSON tabular normalizado

## 4. Stack

- Python 3.10+
- HTTP: curl_cffi (impersonação de TLS de navegador — obrigatório p/ WAF gocache)
- Reprojeção: pyproj (fallback; happy path usa srsName server-side)
- GTFS-RT: gtfs-realtime-bindings (protobuf)
- Metadados/catálogo: modelo de dados próprio inspirado em DCAT (pydantic)
- Testes: pytest

## 5. Decisões decorrentes dos testes (não óbvias)

1. HTTP precisa de impersonação de TLS (curl_cffi) — requests/urllib3 é bloqueado pelo
   WAF gocache da PBH mesmo com User-Agent de navegador.
2. Consulta tabular via Datastore (datastore_search), não via download de CSV.
3. "Recurso mais recente" é problema real no CKAN (snapshot mensal), precisa de heurística.
4. Reprojeção pode ser delegada ao GeoServer (srsName), simplificando o OGCConnector.
5. GTFS-RT exige decoder protobuf — adiciona dependência, mas é padrão internacional.
6. PNCP é a fonte menos confiável hoje: o conector precisa degradar graciosamente.

## 6. Status de implementação

Concluído (funcionando, testado com dados reais):
1. [x] CKANConnector — descoberta + busca + Datastore + latest_resource (snapshot mensal)
2. [x] OGCConnector — WFS GeoJSON + reprojeção server-side (srsName) + filtro CQL
3. [x] RESTConnector (IBGE) — Agregados (dados_simples) + Malhas + Localidades
4. [x] Catálogo DCAT — modelo (pydantic) + CkanHarvester + Catalog (busca)
5. [x] Camada de interoperabilidade — normalize_ibge_code, to_float, per_100k
6. [x] Orquestrador Dataspace — junção cross-source (ex.: academias_por_100k cruza
       BHGEO/WFS com IBGE/REST pelo município)

Pendente:
- [ ] RESTConnector (PNCP) — com retry/backoff (backend instável)
- [ ] GtfsConnector — GTFS estático (S3) + GTFS-Realtime (protobuf)
- [ ] Harvester completo + fichas DCAT das fontes não-CKAN (BHGEO, IBGE, PNCP)
- [ ] Testes de integração + validação da interoperabilidade (sem 10-11)
- [ ] API unificada de consulta (para futura UI de demonstração)
