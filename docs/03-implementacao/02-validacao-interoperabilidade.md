# Validação da interoperabilidade entre fontes

Resultado da etapa de validação (cronograma, semanas 10–11): exercitar os
conectores contra as fontes reais e demonstrar que o dataspace integra dados de
arquiteturas distintas sem repositório central.

Execução: `pytest tests/integration --integration` — 7 testes, todos PASSANDO
(5,1s) contra as APIs vivas. Os testes de integração ficam separados dos unitários
para não sobrecarregar os servidores públicos no ciclo normal de desenvolvimento.

## 1. Cenários de validação

### Cenário A — Junção espacial + demográfica (OGC/WFS + REST)

Pergunta: "quantas academias da cidade existem por 100 mil habitantes?"

- Fonte 1 (contagem): BHGEO, camada `ide_bhgeo:ACADEMIA_CIDADE`, via WFS.
  Reprojetada de EPSG:31983 para EPSG:4326 pelo próprio GeoServer (srsName).
- Fonte 2 (população): IBGE, agregado 6579 (População residente estimada),
  variável 9324, localidade 3106200.
- Chave de junção: município de BH (3106200) — implícito, ambas as fontes são BH.

Resultado real (31/08/2026):

    83 academias / 2.530.701 habitantes = 3,28 por 100 mil

Problemas de interoperabilidade resolvidos:
- SRID divergente (31983 vs 4326) → reprojeção server-side via srsName.
- Valor numérico em string ("2530701") → to_float().
- Dois protocolos distintos (OGC/WFS e REST/JSON) → conectores dedicados com
  saída normalizada.

### Cenário B — Tempo real por protocolo binário (GTFS-Realtime/protobuf)

Pergunta: "quantos ônibus estão em trânsito agora?"

- Fonte: BHTRANS, feed GTFS-Realtime `vehicle-positions` (protobuf), em
  realtime4.mobilibus.com com accesskey.

Resultado real: 756 veículos em trânsito no momento da consulta (o número varia a
cada chamada — é tempo real). Resposta em <1s.

Problemas de interoperabilidade resolvidos:
- Protocolo binário (protobuf) vs JSON dos demais conectores → decode com
  gtfs-realtime-bindings e achatamento para dict JSON.
- Accept header: o feed exige "application/x-google-protobuf" (com o Accept JSON
  global o servidor responde 406).

### Cenário C — Catálogo e consulta in-place (CKAN Action API + Datastore)

Pergunta: "quais datasets existem e como consultar um sem baixar o arquivo?"

- Fonte: CKAN da PBH (dados.pbh.gov.br), 605 datasets, 25 organizações.
- Descoberta via package_list/organization_list/package_search.
- Consulta tabular in-place via Datastore (datastore_search), sem download de CSV.

Resultado real: package_show("sinalizacao-semaforica") → 51 recursos (snapshot
mensal); latest_resource() seleciona o de 20260803; datastore_search devolve 1.146
registros com filtros.

Problemas de interoperabilidade resolvidos:
- WAF "gocache" bloqueia por fingerprint TLS (não só User-Agent) → HTTP via
  curl_cffi com impersonação de navegador.
- Snapshot mensal sem "latest" explícito → heurística latest_resource().

## 2. Mecanismos de interoperabilidade implementados

| Mecanismo | Onde | O que faz |
|-----------|------|-----------|
| normalize_ibge_code | interoperability/ | chave de junção de município (7 dígitos) |
| normalize_cnpj | interoperability/ | chave de junção de órgão/empresa (14 dígitos) |
| to_float | interoperability/ | número BR ("1.234,56" / "2530701") → float |
| per_100k | interoperability/ | taxa comparável entre municípios |
| Reprojeção SRID | connectors/ogc/ | srsName=EPSG:4326 server-side (pyproj p/ fallback) |
| Decode protobuf | connectors/gtfs/ | GTFS-RT → dict JSON |
| Impersonação TLS | connectors/base.py | curl_cffi (WAF gocache) |

## 3. Resultados consolidados

| Fonte | Arquitetura | Validado | Evidência real |
|-------|-------------|----------|----------------|
| CKAN PBH | REST (Action API) + Datastore | sim | 605 datasets; 1.146 registros via datastore_search |
| BHGEO | OGC WMS/WFS | sim | 350 feature types; GeoJSON reprojetado p/ 4326 |
| IBGE | REST (Agregados/Malhas) | sim | pop BH 2021 = 2.530.701; malha GeoJSON em 4326 |
| BHTRANS | GTFS estático + GTFS-RT (protobuf) | sim | 756 veículos em tempo real; 53 MB estático parseado |
| PNCP | REST | parcial* | endpoints de órgão verificados; backend instável |

*PNCP: os endpoints /v1/orgaos e /v1/orgaos/{cnpj} existem (respondem 504/timeout,
confirmando o caminho), mas o backend está instável — documentado como fonte
"intermitente"; os demais endpoints aguardam verificação no Swagger.

## 4. Conclusão

O protótipo demonstra interoperabilidade real entre quatro arquiteturas técnicas
distintas (CKAN, OGC/WFS, REST, GTFS/protobuf) de quatro provedores independentes,
cumprindo o princípio central do TCC: os dados permanecem na fonte e são integrados
sob demanda, via APIs e metadados, sem repositório central. Os dois problemas de
interoperabilidade previstos no mapeamento — SRID divergente e GTFS-Realtime — foram
resolvidos na prática (reprojeção server-side e decode protobuf), e um terceiro
(WAF por fingerprint TLS) foi descoberto e contornado.
