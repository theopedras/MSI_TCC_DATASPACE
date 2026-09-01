# Teste empírico das APIs — resultados reais

Data do teste: 31/08/2026. Método: requisições reais de leitura (GET/HEAD), em volume
controlado, sem operações de escrita. Complementa o inventário documental
(docs/01-mapeamento/) com evidência de request/response real.

Resumo executivo: 4 das 5 fontes responderam de forma plenamente funcional. O PNCP
respondeu, mas com o backend instável (504/timeout). Achado importante: GTFS-Realtime
EXISTE (contradiz o mapeamento, que marcava como "ausência aparente").

## 1. CKAN da PBH

Endpoints: https://dados.pbh.gov.br/api/3/action/ (espelho https://ckan.pbh.gov.br/api/3/action/)

### 1.1 WAF "gocache" bloqueia por fingerprint TLS (ACHADO CRÍTICO)

Sem User-Agent, o WAF "gocache" retorna 403 "Acesso Bloqueado". Com User-Agent de
navegador via curl, responde 200. PORÉM: o mesmo User-Agent via Python requests/urllib3
continua recebendo 403 — o bloqueio é por fingerprint TLS (JA3), não só por header.
O cliente TLS do Python é reconhecido como não-navegador.

Solução: usar curl_cffi com impersonate="chrome" (impersona o TLS de navegador real).
Confirmado: curl_cffi + chrome -> 200, JSON válido. O conector usa curl_cffi por isso
(ver connectors/base.py).

    # requests (urllib3) + User-Agent de navegador -> 403 (bloqueado por TLS)
    # curl_cffi impersonate='chrome'                -> 200

### 1.2 Escala do portal

- package_list: 605 datasets
- organization_list: 25 organizações. Top 5: prodabel_pbh (142), smpu (135), smfa (66),
  smpog (31), smasac (26). (Nota: "smpu" não constava no mapeamento; o portal mudou.)
- group_list: 21 grupos temáticos (topo: mobilidade-urbana 27)
- Formatos (facet res_format, case-sensitive): CSV 548, PDF 541, JSON 29, GeoJSON 1,
  SHAPE 1, HTML 5, ZIP 2. Predomina CSV/PDF; JSON é minoria.

### 1.3 package_search funciona com paginação e filtros

- package_search?rows=N&start=M retorna result.count e result.results
- fq=organization:<org> filtra por organização (confirmado)
- facet.field=["res_format"] retorna facetas (search_facets default vem vazio)

### 1.4 Estrutura de metadados (package_show)

Exemplo "sinalizacao-semaforica":
- license_title: "Creative Commons Attribution", license_id: cc-by (confirmado)
- maintainer: "PRODABEL - Superintendência de Geoprocessamento Corporativo",
  maintainer_email: bhgeo@pbh.gov.br
- extras: VAZIO (não há campos customizados; o mapeamento citava "SRID/periodicidade"
  como metadado, mas não estão em extras)
- num_resources: 51 — um recurso por SNAPSHOT MENSAL (20220601, 20220701, ..., 20260803)

### 1.5 Padrão "snapshot mensal por recurso" (ACHADO)

Datasets históricos não têm um único arquivo "atual": acumulam um recurso CSV por mês.
O conector precisa selecionar o recurso mais recente (por nome/created/last_modified),
não há recurso "latest" explícito.

### 1.6 CKAN Datastore ATIVO (ACHADO)

- datastore_search (resource_id, limit, offset, q, filters, fields) FUNCIONA
  Exemplo: 1073 registros em sinalizacao-semaforica/20220601, campos incluem GEOMETRIA (text)
- datastore_search_sql (SQL bruto) -> 403 Forbidden (SQL desabilitado para público)
- Consequência: dá para consultar dados tabulares SEM baixar CSV, via API de consulta
  (filtros de campo + busca textual + paginação), mas NÃO via SQL.

### 1.7 GTFS estático e GTFS-Realtime

- GTFS estático: ZIP em S3 (https://s3.amazonaws.com/mobilibus-uploads/gtfs/GTFSBHTRANS.zip),
  53,5 MB, atualização semanal (Last-Modified no dia do teste). Download lento deste ambiente
  (~230 KB/s -> ~4 min) — motiva cache local do estático (muda 1x/semana).
- GTFS-Realtime EXISTE (corrige o mapeamento): 3 feeds protobuf (trip-updates,
  vehicle-positions, alerts) em realtime4.mobilibus.com, accesskey na URL.
- vehicle-positions: ~790-818 veículos em trânsito, responde <1s, protobuf ~100 KB.
- Atenção: o feed RT exige Accept "application/x-google-protobuf"; com o Accept JSON
  global (application/json) o servidor devolve 406 Not Acceptable.

## 2. BHGEO / BHMAP (OGC WMS/WFS)

Base: https://bhmap.pbh.gov.br/v2/api/idebhgeo/{wms|wfs} (GeoServer)

- WMS GetCapabilities: 728 KB, 347 camadas nomeadas
- WFS 2.0.0 GetCapabilities: 280 KB, 350 feature types, todos DefaultCRS EPSG:31983

### 2.1 GetFeature em GeoJSON + reprojeção server-side (ACHADO-CHAVE)

O WFS devolve GeoJSON (outputFormat=application/json) e reprojeta no servidor via srsName.

    GET .../wfs?service=WFS&version=2.0.0&request=GetFeature&typeNames=ide_bhgeo:ACADEMIA_CIDADE&count=1&outputFormat=application/json
    -> coord nativa EPSG:31983: [612188.22, 7806899.41]

    GET ...&srsName=urn:ogc:def:crs:EPSG::4326
    -> coord reprojetada EPSG:4326: [-43.92869767, -19.830682]

Consequência arquitetural: a "camada de reprojeção" do dataspace pode ser feita pelo
próprio GeoServer (srsName=EPSG:4326), sem reprojeção cliente-side. pyproj fica como
fallback, não como requisito.

## 3. IBGE

Base: https://servicodados.ibge.gov.br

### 3.1 Agregados (SIDRA)

- /api/v3/agregados -> 70 pesquisas (CD=Censo Demográfico, XF=Estimativas de População, ...)
- Fluxo completo confirmado:
    1. /api/v3/agregados/{id}/metadados  -> variáveis
    2. /api/v3/agregados/{id}/periodos   -> períodos (ex.: 22 períodos)
    3. /api/v3/agregados/{id}/periodos/{p}/variaveis/{v}?localidades=3106200 -> dados

- Exemplo real (agregado 6579 "População residente estimada", variável 9324, 2021):
    Belo Horizonte (3106200) = 2.530.701 pessoas

### 3.2 Malhas (geometria)

- /api/v2/malhas/3106200?formato=application/vnd.geo+json -> FeatureCollection, 1 Polygon
  em EPSG:4326 (WGS84), props {codarea: 3106200, centroide: [-43.9595, -19.9028]}

- Confirma a divergência de SRID: IBGE (4326) vs BHGEO nativo (31983). A ponte é o
  código IBGE do município (3106200) + reprojeção.

## 4. PNCP

Base: https://pncp.gov.br/api/consulta/v1/

Resultado: API alcançável (DNS/TLS OK), mas backend instável no momento do teste:
- GET /api/consulta/v1/orgaos -> 504 Gateway Timeout após ~70s
- GET /api/consulta/v1/orgaos/18715383000140 -> sem resposta em 60s
- Raiz pncp.gov.br -> 302 para www.gov.br/pncp

Implicação: conector PNCP precisa de timeout agressivo + retry/backoff. Documentar como
fonte "intermitente" até nova verificação.

## 5. Correções ao mapeamento (docx da Etapa 1)

1. GTFS-Realtime EXISTE (3 feeds protobuf via mobilibus) — o mapeamento marcava
   "ausência aparente de GTFS-RT" e listava isso como lacuna. LACUNA RESOLVIDA.
2. CKAN Datastore está ativo (datastore_search funciona; SQL bloqueado) — o mapeamento
   não mencionava o Datastore, que muda o desenho do conector (consulta in-place).
3. Metadados "extras" vêm vazios no package_show — os campos "SRID/periodicidade" citados
   no mapeamento não estão em extras do CKAN (a periodicidade pode estar em outro lugar
   ou ser inferida pelo padrão de snapshot mensal).
4. Organizações atuais diferem do mapeamento (ex.: "smpu" com 135 datasets não constava;
   "PRODABEL" agora 142, não 117). O portal evoluiu desde o levantamento.
5. BHGEO WFS reprojeta server-side via srsName — a reprojeção não exige necessariamente
   implementação própria (pyproj), embora pyproj continue útil para malhas/GTFS locais.

## 6. Requisitos técnicos levantados para os conectores

- curl_cffi com impersonação de navegador (o WAF gocache bloqueia requests/urllib3 por TLS)
- Decoder protobuf GTFS-Realtime (lib gtfs-realtime-bindings em Python)
- Reprojeção: server-side via srsName (BHGEO) ou pyproj (malhas IBGE já vêm em 4326)
- Seleção de "recurso mais recente" no padrão de snapshot mensal do CKAN
- Timeout + retry/backoff para PNCP
- Fuso: dados de tempo real (GTFS-RT) em UTC; exibir em America/Sao_Paulo
