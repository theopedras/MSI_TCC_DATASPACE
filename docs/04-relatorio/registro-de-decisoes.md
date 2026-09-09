# Dataspace de Dados Abertos — Belo Horizonte
## Registro de decisões e histórico de desenvolvimento

Trabalho de Conclusão de Curso — MSI-UFMG (POC I/MSI I → POC II/MSI II)
Autor: Theo Lopes Mesquita Pedras
Orientadora: Patrícia Nascimento Silva
Tipo de pesquisa: Tecnológica (protótipo) · Entrega do relatório final: 01/12/2026
Repositório: https://github.com/theopedras/MSI_TCC_DATASPACE

---

## 1. Pergunta de pesquisa e objetivo

Pergunta: como organizar dados e estruturar dataspaces com foco no acesso e reúso pela sociedade?

Objetivo: estruturar e implementar uma arquitetura para dataspaces com foco na organização da informação e em fontes de dados abertos, governamentais e não governamentais.

Princípio central que guia todas as decisões: os dados permanecem na fonte de origem e são integrados sob demanda via APIs e metadados — não por um repositório central que copia tudo.

---

## 2. Linha do tempo (etapas executadas)

O desenvolvimento seguiu o cronograma de 13 semanas do README, com o grosso da implementação concentrado em 31/08/2026 (sessão única) e revisão/consolidação em 08/09/2026.

Etapa 1 — Mapeamento de fontes (agosto/2026)
Inventário exploratório documental das fontes de dados abertos de BH, sem execução de requisições. Produziu o ranking das fontes, a classificação A/B/C/D e a lista inicial de problemas de interoperabilidade. Artefato: docs/01-mapeamento/mapeamento-dataspace-bh.md.

Etapa 2 — Teste empírico das 5 APIs (31/08/2026)
Requisições reais de leitura (GET/HEAD, em volume controlado, sem escrita) às fontes selecionadas. Corrigiu o mapeamento em vários pontos e revelou achados que mudaram o desenho dos conectores. Artefato: docs/03-implementacao/01-teste-apis.md.

Etapa 3 — Arquitetura (31/08/2026)
Esboço da arquitetura fundamentado nos resultados empíricos. Artefato: docs/02-arquitetura/arquitetura.md.

Etapa 4 — Implementação (31/08/2026)
Conectores, catálogo DCAT, camada de interoperabilidade e orquestrador. Sequência de commits:

- 27cee7c — seed inicial: estrutura do repo + Etapa 1 (mapeamento) + proposta
- 0b252e5 — teste empírico das 5 APIs + esboço da arquitetura
- 48a4d4e — CKANConnector (cliente da Action API com impersonação TLS via curl_cffi)
- a6c1f2e — OGCConnector (WFS GeoJSON + reprojeção) e IbgeConnector (Agregados + Malhas)
- b638b45 — catálogo DCAT + camada de interoperabilidade + orquestrador Dataspace
- 849604b — GtfsConnector (estático S3 + GTFS-Realtime protobuf)
- da03ae1 — PncpConnector (órgãos por CNPJ + timeout curto + retry/backoff)
- 4e79fa2 — testes de integração (pytest --integration) + doc de validação

Etapa 5 — Validação da interoperabilidade (31/08/2026)
7 testes de integração contra as APIs reais, todos passando, demonstrando junções entre arquiteturas distintas. Artefato: docs/03-implementacao/02-validacao-interoperabilidade.md.

---

## 3. Registro de decisões

| # | Decisão | Contexto / racional | Consequência |
|---|---------|---------------------|--------------|
| 1 | Dado permanece na fonte, integrado via API/metadados | Princípio do enunciado do TCC; copiar para repositório central contradiz o propósito do dataspace | Nenhum dado é replicado; conectores consultam sob demanda |
| 2 | Selecionar 5 fontes cobrindo 4 arquiteturas técnicas distintas (CKAN, OGC/WFS, REST, arquivo/protobuf) | Mais valioso academicamente que 5 fontes "fáceis": força implementar mais de um tipo de conector e demonstra o conceito de dataspace de forma robusta | CKAN PBH, BHGEO, IBGE, PNCP, GTFS BHTRANS |
| 3 | Conectores reutilizáveis por arquitetura, não por fonte | Um conector CKAN serve PBH e MG; um REST serve IBGE e PNCP | 4 conectores cobrem 5 fontes + escalam para Nível 2/3 (RMBH/Brasil) |
| 4 | UI é CONSUMIDORA, não núcleo do dataspace | Priorizar o core (conectores + catálogo + interoperabilidade + API unificada); UI fina só se sobrar tempo | Escopo travado; evita dispersão nas semanas finais |
| 5 | HTTP via curl_cffi com impersonação de navegador | ACHADO EMPÍRICO: o WAF "gocache" do CKAN PBH bloqueia por fingerprint TLS (JA3), não só por User-Agent — requests/urllib3 recebe 403 mesmo com UA de navegador | BaseConnector usa curl_cffi; todos os conectores herdaram a solução |
| 6 | Consulta tabular via Datastore (datastore_search), não download de CSV | Datastore ativo; datastore_search_sql (SQL bruto) devolve 403 | Consulta in-place com filtros de campo, sem baixar arquivo |
| 7 | Heurística latest_resource() para "recurso mais recente" | CKAN acumula um CSV por snapshot mensal (ex.: sinalização semafórica, 51 recursos); não existe recurso "latest" explícito | Conector seleciona o snapshot mais novo por created/last_modified/parse do nome |
| 8 | Reprojeção server-side via srsName=EPSG:4326 | BHGEO reprojeta no próprio GeoServer; dispensa reprojeção cliente-side | pyproj vira fallback (malhas/GTFS locais), não requisito do happy path |
| 9 | Decodificar GTFS-Realtime com gtfs-realtime-bindings | ACHADO EMPÍRICO: GTFS-RT EXISTE (3 feeds protobuf em mobilibus), contrariando o mapeamento que marcava "ausência" | +1 dependência (padrão internacional), mas corrige uma lacuna real |
| 10 | Override de Accept por requisição no GTFS | O feed RT exige `application/x-google-protobuf`; com o Accept JSON global o servidor devolve 406 | GtfsConnector ajusta o header por chamada (mesmo padrão p/ download do ZIP) |
| 11 | PNCP: timeout curto (20s) + retry/backoff (2s) | Backend instável no teste (504/timeout ~70s); fonte intermitente, não "quebrada" | Conector degrada graciosamente (~21s p/ 2 tentativas) em vez de travar |
| 12 | Modelo de catálogo inspirado em DCAT (W3C), em pydantic | Padrão aberto de metadados; harvester do CKAN + fichas manuais p/ fontes não-CKAN | Dataset/Distribution/Publisher; busca unificada no catálogo |
| 13 | Chave de junção universal = código IBGE do município (3106200 = BH) | Único identificador compartilhado entre fontes heterogêneas; CNPJ como chave secundária p/ compras | Junções cross-source (ex.: academias por 100k = BHGEO × IBGE) |
| 14 | Normalização de saída: SRID→4326, fuso America/Sao_Paulo, GeoJSON/JSON | Interoperabilidade na borda do dataspace; cada fonte entrega formato próprio | Camada interoperability/normalize.py centraliza as conversões |
| 15 | Testes de integração separados e skipados por padrão | Não sobrecarregar servidores públicos no ciclo normal de desenvolvimento | `pytest` roda só unitários; `pytest --integration` bate nas APIs reais |
| 16 | Fontes sem API (TabNet/DATASUS, partes do Portal da Transparência) fora do protótipo | Exigiriam ETL/scraping, violando o princípio "dado na fonte" | Documentadas como lacuna/oportunidade futura, não como fonte do 1º protótipo |

---

## 4. Achados empíricos que mudaram o curso

Diferenças entre o mapeamento documental (Etapa 1) e a realidade das APIs (Etapa 2), que redesenharam a implementação:

1. WAF por fingerprint TLS no CKAN PBH — não documentado; requests/urllib3 bloqueado. Contornado com curl_cffi + impersonate="chrome".
2. CKAN Datastore ativo — o mapeamento não o citava; habilitou consulta in-place e mudou o desenho do conector.
3. Snapshot mensal sem "latest" — o mapeamento não previu; exigiu heurística de seleção do recurso mais recente.
4. GTFS-Realtime existe — o mapeamento marcava "ausência aparente" e listava como lacuna; lacuna resolvida na prática.
5. BHGEO reprojeta server-side (srsName) — a "camada de reprojeção" prevista virou delegação ao GeoServer, não implementação própria.
6. Metadados "extras" vêm vazios no package_show — os campos "SRID/periodicidade" citados no mapeamento não estão lá.
7. Organizações do portal evoluíram — "smpu" (135 datasets) não constava; PRODABEL foi de 117 para 142.

Lição registrada: sempre confirmar endpoints empiricamente; documentação oficial (e o próprio mapeamento da Etapa 1) pode estar defasada.

---

## 5. Estado atual

Implementado e validado com dados reais:
- 4 conectores (CKAN, OGC, REST/IBGE+PNCP, GTFS) cobrindo 5 fontes
- Catálogo DCAT (modelo pydantic + CkanHarvester + busca)
- Camada de interoperabilidade (normalize_ibge_code, normalize_cnpj, to_float, per_100k)
- Orquestrador Dataspace (junções cross-source)
- 51 testes unitários + 7 de integração, todos verdes

Validação em números (31/08/2026):
- Cenário A: 83 academias / 2.530.701 habitantes = 3,28 por 100 mil (join OGC/WFS × REST/IBGE)
- Cenário B: 756 ônibus em trânsito em tempo real (GTFS-Realtime/protobuf, <1s)
- Cenário C: 605 datasets, 1.146 registros via Datastore sem download

Pendências (documentadas na arquitetura, seção 6):
- Verificar endpoints adicionais do PNCP (contratações, atas, licitações) quando o backend voltar
- Harvester completo + fichas DCAT das fontes não-CKAN (BHGEO, IBGE, PNCP)
- API unificada de consulta (pré-requisito da UI de demonstração)

---

## 6. Estrutura do repositório (onde está cada coisa)

- docs/projeto/ — proposta formal (PDF)
- docs/01-mapeamento/ — inventário Etapa 1
- docs/02-arquitetura/arquitetura.md — arquitetura + modelo DCAT
- docs/03-implementacao/01-teste-apis.md — resultados empíricos dos testes
- docs/03-implementacao/02-validacao-interoperabilidade.md — validação
- connectors/ — BaseConnector + conectores CKAN/OGC/REST/GTFS
- catalog/ — modelos DCAT + harvester + busca
- interoperability/ — normalização de chaves e formatos
- dataspace.py — orquestrador
- tests/ — unitários + integração

---

## 7. Link do GitHub

https://github.com/theopedras/MSI_TCC_DATASPACE
