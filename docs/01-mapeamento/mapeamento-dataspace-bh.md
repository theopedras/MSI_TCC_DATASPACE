# Mapeamento de APIs e Fontes de Dados Abertos de Belo Horizonte para Construção de um Dataspace
Documento: Inventário técnico exploratório (Etapa 1 do TCC) Data do levantamento: agosto de 2026 Metodologia: pesquisa documental em fontes primárias (portais oficiais, documentação técnica de APIs, manuais de integração) via busca web. Nenhum endpoint foi inventado; onde a confirmação direta não foi possível, o item está marcado como "Não confirmado".

## 1. Resumo executivo
Belo Horizonte tem uma base de dados abertos mais madura do que a média dos municípios brasileiros. O eixo central é o Portal de Dados Abertos da PBH (dados.pbh.gov.br, espelhado tecnicamente em ckan.pbh.gov.br), rodando sobre CKAN, que expõe uma API REST/JSON documentada e sem autenticação (/api/3/action/...) e reúne dezenas de organizações municipais (PRODABEL, BHTRANS, BELOTUR, SMED, SMFA, SMMA, SMOBI, SMPOG, FMC, FPMZB, Hospital Odilon Behrens, Defesa Civil, Controladoria etc.), cobrindo mobilidade, finanças, licitações, meio ambiente, cultura, turismo, educação e assistência social. Este portal é o candidato mais forte a primeira fonte do dataspace, por já ser interoperável (padrão CKAN, replicado automaticamente para dados.gov.br).
Paralelamente, BH mantém uma Infraestrutura de Dados Espaciais própria (BHGEO/BHMAP), com serviços WMS e WFS no padrão OGC, o que a torna, junto com o CKAN, a segunda coluna vertebral técnica do dataspace (dados geoespaciais interoperáveis por desenho).
Para mobilidade em tempo real, a BHTRANS publica GTFS estático e um dataset de coordenadas de ônibus atualizado a cada 20 segundos, ambos via CKAN — sem necessidade de autenticação — e existe pelo menos um projeto de terceiros (OpenBHBus) que já demonstra o consumo desses dados via API REST.
No nível estadual e federal, os candidatos mais relevantes para complementar o dataspace são: IBGE (API de Agregados/SIDRA e API de Localidades/Malhas, ambas REST/JSON, sem autenticação, muito bem documentadas), INMET (dados meteorológicos, com portal de API e BDMEP), Portal Nacional de Contratações Públicas — PNCP (API REST/JSON obrigatória para todos os entes desde a Lei 14.133/2021, cobrindo licitações e contratos de BH), e o Portal de Dados Abertos de Minas Gerais (dados.mg.gov.br, também CKAN), que traz segurança pública (crimes violentos, por município) e outras séries estaduais.
Fontes de acesso não estruturado ou "Não confirmado" também foram identificadas (ex.: parte dos dados do Portal da Transparência da PBH aparecem apenas como páginas HTML/relatórios, não API própria — a via estruturada é o CKAN), e devem ser tratadas como oportunidades futuras, não como participantes de um primeiro protótipo.
A recomendação central deste inventário é que o protótipo acadêmico comece por 3 a 5 fontes já dotadas de API REST documentada e sem barreira de autenticação — CKAN da PBH, GTFS/tempo-real da BHTRANS, WFS do BHGEO, API de Agregados do IBGE e, opcionalmente, a API de consulta do PNCP — porque juntas elas já permitem demonstrar interoperabilidade real entre quatro provedores distintos (municipal tabular, municipal geoespacial, municipal transporte e federal estatístico/contratual) sem exigir nenhuma etapa de scraping.

## 2. Mapa das principais fontes de dados de Belo Horizonte
NÍVEL 1 — BELO HORIZONTE (município)
├── Prefeitura de BH (PBH) — guarda-chuva institucional
│   ├── Portal de Dados Abertos PBH (CKAN) ─────────── API REST/JSON, sem auth
│   │     ├── PRODABEL (TI, geoprocessamento, 1746/SDM) — 117 datasets
│   │     ├── BHTRANS (mobilidade, trânsito, GTFS)      — 24 datasets
│   │     ├── SMFA (finanças, tributos)                 — 58 datasets
│   │     ├── SMPOG (planejamento, orçamento)           — 29 datasets
│   │     ├── SMED (educação)                           — 20 datasets
│   │     ├── SMMA / SMASAC (meio ambiente / assist. social) — 23 c/u
│   │     ├── SMOBI (obras e infraestrutura)            — 10 datasets
│   │     ├── BELOTUR (turismo)                         — 11 datasets
│   │     ├── FMC (cultura), FPMZB (parques/zoobotânica), SMDE, SMEL, CGM, Defesa Civil, HOB
│   ├── BHGEO / BHMAP — geoprocessamento (WMS/WFS, OGC) — dado espacial estruturado
│   ├── Portal da Transparência PBH — finanças, licitações, obras (HTML/CKAN)
│   └── Câmara Municipal de BH (CMBH) — portal de transparência próprio (Não confirmado: API)
├── Empresas/autarquias municipais (dados via CKAN acima): SLU, SUDECAP, URBEL, PBH Ativos
NÍVEL 2 — REGIÃO METROPOLITANA DE BH (RMBH)
├── Agência RMBH (Agência de Desenvolvimento da RMBH) — portal de transparência (Não confirmado: dados abertos estruturados)
└── Demais 33 municípios da RMBH — portais próprios heterogêneos (fora do escopo desta etapa)
NÍVEL 3 — MINAS GERAIS / BRASIL (fontes usadas para enriquecer/comparar dados de BH)
├── Portal de Dados Abertos de MG (dados.mg.gov.br, CKAN) — segurança pública (crimes violentos por município), outros
├── SEJUSP/MG — Observatório de Segurança Pública (Armazém SIDS/REDS)
├── IBGE — API de Agregados (SIDRA), API de Localidades/Malhas Geográficas — REST/JSON, sem auth
├── DATASUS/TabNet — saúde, agregada por município (interface web, não API REST tradicional)
├── INMET — dados meteorológicos (API + BDMEP)
├── ANEEL — dados abertos de energia (CKAN + ArcGIS Open Data)
├── PNCP — Portal Nacional de Contratações Públicas — API REST/JSON obrigatória (Lei 14.133/2021)
├── Portal da Transparência do Governo Federal — API de dados (requer token por e-mail)
├── Portal Brasileiro de Dados Abertos (dados.gov.br) — replica o catálogo da PBH via API própria
└── Catálogo de Dados Abertos (catalogodedadosabertos.com.br) — catálogo curado (ECI/UFMG), majoritariamente federal (BACEN, IBGE, IPEA, SUS, Transparência, Senado etc.) — referência para o desenho da camada de metadados/catálogo do dataspace

## 3. Tabela completa de fontes, APIs e datasets
Legenda de confiabilidade: [D] = confirmado em documentação oficial; [T] = confirmado tecnicamente (ex.: exemplo de endpoint em manual/paper), mas não testado nesta etapa; [NC] = Não confirmado (endpoint/API não localizado com certeza — registrado apenas como pista).

| Nome da fonte | Órgão responsável | Dataset(s) principal(is) | Categoria | Escopo | API? | URL da API | Documentação | Autenticação | Formato | Protocolo | Método de acesso | Atualização | Histórico | Metadados | Identificadores | Licença | Interoperabilidade | Potencial | Observações |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Portal de Dados Abertos PBH | PBH (multi-secretarias) | Centenas de datasets (todas categorias) | Multi | BH | Sim [D] | https://dados.pbh.gov.br/api/3 (espelho ckan.pbh.gov.br) | databh.pbh.gov.br/dados-abertos | Nenhuma para leitura | CSV, JSON, XML, GeoJSON, PDF | REST (CKAN Action API) | API + download + CKAN | Variável por dataset (mensal a tempo real) | Parcial (por dataset) | Título, descrição, periodicidade, órgão, licença, formato, SRID (EPSG:31983) | ID do dataset/recurso (CKAN UUID) | Predominante CC-BY | Alta — padrão CKAN, sincronizado com dados.gov.br desde 2020 (INDA) | Alto | Fonte-âncora do dataspace municipal |
| BHTRANS — GTFS Convencional/Suplementar | BHTRANS (via CKAN PBH) | GTFS estático (linhas, paradas, horários) | Mobilidade | BH | Sim [D] | via dados.pbh.gov.br (dataset gtfs) | Documentação GTFS padrão + portal PBH | Nenhuma | ZIP (arquivos texto GTFS) | Download estruturado | CKAN/download | Semanal | Versões anteriores mantidas como datasets "desativados" | Periodicidade, órgão, formato | route_id, stop_id, trip_id (padrão GTFS) | CC-BY (a confirmar por dataset) | Alta — GTFS é padrão internacional (Google/ MobilityData) | Alto | Listado também no Mobility Database (mdb-9) |
| BHTRANS — Tempo Real Ônibus (coordenadas) | BHTRANS (via CKAN PBH) | Posição dos ônibus | Mobilidade / Trânsito | BH | Sim [D] | dados.pbh.gov.br/dataset/tempo_real_onibus_-_coordenada | Portal PBH | Nenhuma | Arquivo de coordenadas (download) | Download periódico | CKAN/download | A cada 20 segundos | Não (fluxo contínuo) | Periodicidade, formato | Placa/linha, coordenadas | A confirmar | Média-alta — não é streaming API, mas download recorrente | Alto | Usado pelo projeto open-source "Cadê Meu Busão" (tarifazero/monitoramento) |
| OpenBHBus (terceiros) | Projeto comunitário (não oficial) | Linhas, tarifas, horários, itinerários | Mobilidade | BH/RMBH | Sim [T] | https://openbhbus.herokuapp.com | Repositório GitHub lucasparreiras/OpenBHBUs | Nenhuma (aparente) | JSON | REST | API | Depende da fonte original (BHTRANS) | Não documentado | Baixo (projeto de terceiros) | Linha/itinerário | GNU GPL 3.0 | Baixa (não oficial, dependente de disponibilidade do serviço) | Médio (prova de conceito, não fonte primária) | Não é fonte oficial; útil como referência de design de API, não como fonte de produção |
| BHGEO / BHMAP — Serviços Geográficos | PRODABEL/PBH | Camadas geoespaciais diversas (endereços, uso do solo, equipamentos urbanos etc.) | Geolocalização / Uso do solo | BH | Sim [D] | WMS: bhmap.pbh.gov.br/v2/api/idebhgeo/wms; WFS: bhmap.pbh.gov.br/v2/api/idebhgeo/wfs | Portal BHGEO (prefeitura.pbh.gov.br/bhgeo) + GeoServer docs | Nenhuma para consulta pública | GML/GeoJSON (WFS), imagem PNG/JPEG (WMS) | OGC WMS/WFS | API (padrão OGC), plugável em QGIS/ArcGIS | Variável (diária a eventual) | Catálogo de metadados via GeoNetwork | Ficha de metadado por camada (GeoNetwork) | Código de camada IDE-BHGEO | A confirmar | Alta — padrão OGC + INDE (BH foi o 1º município a aderir à INDE, 2015) | Alto | SRID padrão EPSG:31983 (SIRGAS 2000 zona local) |
| PRODABEL — 1746/SDM (chamados) | PRODABEL/PBH | Tickets de solicitação de serviço e incidentes | Serviços públicos | BH | Sim [D] (via CKAN) | dados.pbh.gov.br (organização PRODABEL, tag "sdm") | Plano de Dados Abertos PRODABEL 2020-2021 (PDF) | Nenhuma | CSV | Download/CKAN | Periódica (a confirmar granularidade) | Histórico por período de publicação | Periodicidade, órgão | ID do chamado | CC-BY (a confirmar) | Média | Médio-Alto | Relaciona-se com localização (endereço) e categoria de serviço |  |
| Portal da Transparência PBH | Controladoria-Geral do Município / SMFA | Despesas, receitas, licitações, contratos, obras, dívida, folha de pagamento, PPAG, LDO/LOA | Finanças públicas / Compras / Obras | BH | Parcial [T] | Não há endpoint REST próprio confirmado; dados estruturados redirecionam para o CKAN da PBH | prefeitura.pbh.gov.br/transparencia | N/A (páginas HTML) para navegação; CKAN para os datasets exportáveis | HTML, CSV, PDF (via CKAN) | Portal web + CKAN | Portal + CKAN | Mensal/anual conforme peça orçamentária | Sim (por exercício) | Glossário disponível no portal | Nº de processo, empenho, contrato | A confirmar | Média (depende do CKAN para estruturação) | Médio-Alto | Tratar como "fonte com acesso estruturado via CKAN", não como API própria dedicada |
| Câmara Municipal de BH (CMBH) — Transparência | CMBH | Execução orçamentária/financeira da Câmara | Finanças públicas | BH | Não confirmado [NC] | — | cmbh.mg.gov.br/transparencia-principal | — | HTML/PDF (aparente) | Portal web | — | — | — | — | — | Baixa (sem API aparente) | Baixo (nesta etapa) | Requer investigação futura |  |
| Agência RMBH — Portal de Compras/Transparência | Agência de Desenvolvimento da RMBH | Licitações, prestação de contas | Finanças / Compras | RMBH | Não confirmado [NC] | — | agenciarmbh.mg.gov.br/transparencia | — | HTML/PDF (aparente) | Portal web | — | — | — | — | — | Baixa | Baixo | Relevante para demonstrar expansão futura Nível 2 |  |
| Portal de Dados Abertos de MG | Governo do Estado de MG (CKAN) | Diversos, incl. Crimes Violentos por município (SEJUSP) | Segurança pública / Multi | MG (inclui BH) | Sim [D] | dados.mg.gov.br (CKAN Action API, padrão igual ao da PBH) | dados.mg.gov.br | Nenhuma | CSV/JSON via CKAN | REST (CKAN) | API/download | Mensal (a confirmar por dataset) | Sim (séries históricas) | Órgão fonte: Observatório de Segurança Pública/SEJUSP | Código do município (IBGE) | A confirmar | Alta (mesmo padrão CKAN da PBH → facilita join técnico) | Alto | Excelente par para demonstrar interoperabilidade entre dois CKANs de níveis distintos |
| SEJUSP/MG — Armazém SIDS/REDS | Secretaria de Justiça e Segurança Pública de MG | Registro de Evento de Defesa Social (REDS), crimes violentos, feminicídio | Segurança pública | MG (dados por município, incl. BH) | Parcial [T] | Publicado como planilha/dataset dentro do CKAN de MG | seguranca.mg.gov.br/.../dados-abertos | Nenhuma para os arquivos | XLSX/CSV | Download (via CKAN de MG) | Mensal | Sim | Definição de campos do REDS publicada | Código do município | A confirmar | Média (dado agregado, não API dedicada) | Médio | Fonte primária estadual; nível de granulação até o município |  |
| SINESP (Ministério da Justiça) | Secretaria Nacional de Segurança Pública (SENASP/MJSP) | Ocorrências criminais nacionais, Dados Nacionais de Segurança Pública | Segurança pública | Brasil (agregável a MG/BH) | Sim, mas restrito [T] | Dataset publicado em dados.mj.gov.br; acesso operacional ao Sinesp Integração requer cadastro aprovado | dados.mj.gov.br/dataset/sistema-nacional-de-estatisticas-de-seguranca-publica | Cadastro/aprovação para módulos operacionais; dataset aberto sem auth | CSV/XLSX | Download (dados.gov.br/CKAN) | Mensal, com defasagem de ~3 meses para consolidação | Sim, desde 2015 (Sinesp Integração) | Manual metodológico disponível | Código UF/Município | A confirmar | Média | Médio | Complementar ao dado estadual (SEJUSP), útil para escala nacional futura |  |
| IBGE — API de Agregados (SIDRA) | IBGE | Censos, PNAD, contagens populacionais, indicadores socioeconômicos por município | População / Demografia / Economia | Brasil (filtrável por município, incl. BH — código 3106200) | Sim [D] | https://servicodados.ibge.gov.br/api/v3/agregados | servicodados.ibge.gov.br/api/docs/agregados?versao=3 | Nenhuma | JSON | REST | API direta | Depende da pesquisa (Censo: decenal; PNAD contínua: trimestral) | Sim, por período/tabela SIDRA | Metadados completos por agregado (período, variável, classificação, categoria) via endpoint /metadados | Código de agregado (tabela SIDRA), código IBGE do município | Dados públicos, uso livre com citação | Alta — API é referência de boas práticas em dados agregados governamentais no Brasil | Alto | 17 APIs de serviço IBGE catalogadas (Agregados, Localidades, Malhas, CNAE, Calendário etc.) |
| IBGE — API de Localidades e Malhas Geográficas | IBGE | Divisão territorial, malhas municipais em GeoJSON | Geolocalização / Uso do solo | Brasil (BH incluso) | Sim [D] | https://servicodados.ibge.gov.br/api/v2/malhas/{municipio} ; .../v1/localidades/... | servicodados.ibge.gov.br/api/docs | Nenhuma | GeoJSON | REST | API direta | Baixa frequência (malhas mudam pouco) | Por edição de malha | Resolução, qualidade, formato | Código IBGE do município (BH = 3106200) | Uso livre | Alta — geometria oficial padronizada, chave de junção universal | Alto | Peça central para o "identificador comum" do dataspace (código de município) |
| DATASUS / TabNet — Saúde | Ministério da Saúde | Morbidade, mortalidade, nascidos vivos, indicadores de saúde por município | Saúde | Brasil (agregável a BH) | Parcial [NC/T] | Não há API REST tradicional confirmada para o TabNet; acesso via interface web tabuladora | datasus.saude.gov.br/informacoes-de-saude-tabnet | Nenhuma para consulta | HTML tabulado, exportável CSV/DBF | Interface web (tabulador), não API REST clássica | Portal/tabulação manual, scraping possível mas não recomendado como 1ª escolha | Mensal/anual conforme base | Sim, séries históricas longas | Dicionário de dados por sistema (SIH, SIM, SINASC etc.) | CID, CNES, código de município | Uso público | Média — dados robustos, mas acesso tecnicamente pouco amigável a integração automática | Médio | Boa fonte para enriquecer o dataspace, mas exige camada de transformação (não é API nativa) |
| e-SUS / OpenDataSUS | Ministério da Saúde (via Catálogo ODA) | Diversos (imunização, atenção básica) | Saúde | Brasil | Sim [D] (catalogado) | Listado no Catálogo de APIs de Dados Abertos (ECI/UFMG) | catalogodedadosabertos.com.br | Variável | JSON/CSV | REST | API | Variável | Sim | A confirmar | CNES, CNPJ, código de município | A confirmar | Média-alta | Médio | Relevante para complementar saúde a nível nacional |
| INMET — Dados Meteorológicos | Instituto Nacional de Meteorologia | Observações de estações automáticas/convencionais, previsão do tempo | Clima / Meio ambiente | Brasil (estação de BH/Minas Gerais aplicável) | Sim [D] | Portal com API (portal.inmet.gov.br); BDMEP (bdmep.inmet.gov.br) para séries históricas | portal.inmet.gov.br/manual | Nenhuma para consulta pública | JSON/CSV | REST (API) + download BDMEP | API + portal de download | Estações automáticas: horária; convencionais: 3x/dia | Sim, séries históricas longas (BDMEP) | Normas técnicas OMM referenciadas | Código da estação (ex.: A521 para BH) | Uso público | Alta — padrão internacional (OMM/WIGOS) | Alto | Nenhuma estação é exclusiva de BH, mas há estações no município/RMBH |
| ANEEL — Dados Abertos de Energia | Agência Nacional de Energia Elétrica | Geração distribuída, tarifas, licitações do setor elétrico | Energia | Brasil (filtrável por distribuidora/município) | Sim [D] | dadosabertos.aneel.gov.br (CKAN) + portal ArcGIS Open Data | dadosabertos.aneel.gov.br | Nenhuma | CSV/JSON/GeoJSON | REST (CKAN) + ArcGIS REST (geo) | API | Variável | Sim | Boa (Plano de Dados Abertos publicado) | CNPJ da distribuidora, código de município | Aberta | Alta (CKAN, mesmo padrão de PBH/MG) | Médio | CEMIG é a distribuidora local; dados desagregam por município via essa base nacional |
| PNCP — Portal Nacional de Contratações Públicas | Ministério da Gestão/ENAP (gestão nacional) | Editais, contratos, atas de registro de preço, planos de contratação — de todos os órgãos, incl. PBH | Compras públicas / Licitações / Contratos | Brasil (filtrável por CNPJ do órgão — PBH e suas empresas) | Sim [D] | Base: https://pncp.gov.br/api/consulta (consultas públicas); https://pncp.gov.br/api/pncp (manutenção, autenticada) | pncp.gov.br/manual/pt-br/latest/singlehtml + Swagger (pncp.gov.br/api/consulta/swagger-ui) | Nenhuma para consulta; login/token JWT para inserção/alteração | JSON | REST | API direta | Praticamente em tempo real (obrigatório por lei) | Sim, desde vigência da Lei 14.133/2021 | Manual de Integração v2.5 muito detalhado | CNPJ do órgão, nº de processo/contratação/ata | Uso público | Alta — obrigatório e padronizado nacionalmente | Alto | Excelente fonte para casar "licitações/compras" (categoria pedida no TCC) com CNPJ de empresas |
| dados.gov.br — Portal Brasileiro de Dados Abertos | Governo Federal (INDA) | Réplica de todos os datasets publicados nos CKANs aderentes (incl. PBH) + organizações federais próprias | Multi | Brasil (inclui espelho de BH) | Sim [D] | Swagger produção: dados.gov.br/swagger-ui/index.html | mesmo | Requer Conecta gov.br para alguns serviços; leitura de catálogo é aberta | JSON | REST | API | Reflete a fonte original | Depende da fonte | Bom (padrão DCAT) | ID do dataset (harvest) | Predominante ODbL/CC | Alta (é a camada de catálogo nacional) | Alto (como catálogo, não fonte primária) | Interessante como inspiração/participante da camada "Catálogo/Metadados" do dataspace |
| Catálogo de Dados Abertos (ECI/UFMG) | Observatório de Dados Abertos (ECI/UFMG, financiado FAPEMIG) | Curadoria de ~15 APIs federais (BACEN, IBGE, IPEA, SUS, Transparência, Senado, CadPrev, SALIC, SADIPEM etc.) | Multi (majoritariamente federal) | Brasil (não específico de BH) | Sim (curadoria de APIs de terceiros) | Ver catalogodedadosabertos.com.br/Apismapeadas | catalogodedadosabertos.com.br/Apis | Variável por API listada | Variável | Variável | Catálogo/documentação | N/A | N/A | Alto nível de detalhe técnico por API (é o próprio objetivo do catálogo) | N/A | N/A | Não é fonte de dados de BH, mas é referência direta de arquitetura de catálogo citada no enunciado do TCC | Alto (como modelo de catálogo, não como fonte) | Não confundir com fonte de dados — é meta-catálogo |
| Portal da Transparência do Governo Federal | CGU | Despesas, contratos, convênios, servidores federais (poucos filtráveis a BH diretamente, exceto órgãos federais sediados na cidade) | Finanças públicas | Brasil | Sim [D] | api.portaldatransparencia.gov.br | portaldatransparencia.gov.br/api-de-dados | Token por e-mail obrigatório | JSON | REST | API | Diária/mensal conforme endpoint | Sim | Boa | CNPJ/CPF, código de órgão | Uso público mediante cadastro | Alta (API nacional de referência) | Médio (baixa relevância direta para BH, mas útil para servidores/órgãos federais locais) | Primeira API brasileira de transparência com token, referência de modelo de autenticação leve |


## 4. Análise técnica das APIs mais relevantes

### 4.1 CKAN da PBH (dados.pbh.gov.br / ckan.pbh.gov.br)
Endpoint base: https://dados.pbh.gov.br/api/3/action/
Endpoints confirmados [D]:
package_list — lista todos os datasets
package_show?id=<dataset> — detalhes de um dataset (título, descrição, recursos/arquivos)
resource_show?id=<recurso> — detalhes de um recurso específico
tag_list — lista de tags/temas
Método HTTP: GET (padrão CKAN Action API é majoritariamente GET para leitura; POST para escrita, não aplicável a consumidores externos)
Parâmetros: q (busca textual), fq (filtros avançados, ex. por data/categoria/organização)
Formato de resposta: JSON, envelope padrão CKAN {"success": bool, "result": {...}}
Paginação: suportada nativamente pelo CKAN via rows/start em package_search (endpoint adicional do padrão CKAN, não citado explicitamente na documentação da PBH consultada, mas herdado do software CKAN)
Autenticação: nenhuma para leitura pública
Limites de requisição: a documentação da PBH menciona "limitações de taxa de acesso para evitar sobrecarga", sem número explícito publicado — Não confirmado o valor exato
Versionamento: API versão 3 (/api/3/), padrão do software CKAN
Estabilidade/disponibilidade: alta — é infraestrutura oficial e replicada para o Portal Brasileiro de Dados Abertos
Consulta incremental/sincronização: possível via filtro por data de atualização do metadado do pacote (campo metadata_modified, padrão CKAN), mas não documentada explicitamente pela PBH — tratar como inferência técnica, não fato confirmado
Relacionamento com outros datasets: dentro do próprio portal, datasets se relacionam por organização (secretaria) e por grupo temático (ex. grupo "mobilidade-urbana"); entre portais, a chave de relação universal é o código do município IBGE (3106200), quando presente nos metadados de cada dataset — isso precisa ser verificado dataset a dataset, pois nem todos os recursos trazem esse código explicitamente

### 4.2 BHGEO/BHMAP — WMS/WFS
Endpoint WMS: https://bhmap.pbh.gov.br/v2/api/idebhgeo/wms
Endpoint WFS: https://bhmap.pbh.gov.br/v2/api/idebhgeo/wfs
Padrão: OGC (GeoServer), com operações GetCapabilities, GetMap (WMS) e GetFeature (WFS)
Exemplo de requisição documentado: https://bhmap.pbh.gov.br/v2/api/servico/imagemap?width=800&height=600&format=png&fator=2&layersbase=ide_bhgeo:MAPA_BASE&layer=ide_bhgeo:TRECHO_L... (exemplo truncado na fonte, mas confirma o padrão de camadas nomeadas ide_bhgeo:<CAMADA>)
Formato de resposta: imagem (PNG/JPEG/GIF) via WMS; GML/GeoJSON via WFS
SRID: EPSG:31983 (SIRGAS 2000, projeção UTM zona 23S) — importante ponto de atenção para interoperabilidade, pois a maioria das APIs nacionais (IBGE, INDE) trabalha em EPSG:4326 (WGS84); qualquer integração exige camada de reprojeção
Autenticação: nenhuma para consulta pública
Metadados: catalogados separadamente via GeoNetwork (catálogo de metadados geoespaciais), com ficha própria por camada
Consulta incremental: não documentada; WFS permite filtros espaciais (bbox) e atributos via GetFeature com parâmetro filter, padrão OGC

### 4.3 GTFS e tempo real BHTRANS
GTFS estático: arquivo ZIP (padrão internacional Google/MobilityData), atualizado semanalmente, distribuído como recurso dentro de um dataset CKAN (não é uma API de consulta, é um artefato de download versionado)
Tempo real (coordenadas): dataset separado, atualizado a cada 20 segundos, também distribuído como arquivo de download recorrente — não é um streaming/API push; é "polling" sobre um recurso estático que a PBH atualiza continuamente
Observação técnica relevante: BH não parece publicar GTFS-Realtime (protobuf, padrão para posição de veículos em tempo real usado por Google Maps/Moovit) — os dados de tempo real são distribuídos em formato próprio de coordenadas, não no padrão GTFS-RT. Isso é uma lacuna de interoperabilidade a ser investigada na próxima etapa.
Relacionamento com outros datasets: stop_id/route_id do GTFS podem, em tese, ser cruzados com os pontos de embarque/desembarque, sinistros de trânsito e áreas de estacionamento rotativo publicados separadamente pela BHTRANS no mesmo CKAN — todos usam malha viária de BH como referência espacial comum (SRID EPSG:31983)

### 4.4 IBGE — API de Agregados (SIDRA)
Endpoint base: https://servicodados.ibge.gov.br/api/v3/agregados
Endpoints documentados [D]:
/agregados — lista agregados agrupados por pesquisa
/agregados/{agregado}/localidades/{nivel} — localidades associadas a um agregado
/agregados/{agregado}/metadados — metadados do agregado
/agregados/{agregado}/periodos — períodos disponíveis
/agregados/{agregado}/periodos/{periodos}/variaveis/{variavel} — dados efetivos
Ferramenta de apoio: "Query Builder" na própria documentação, que monta a URL da consulta visualmente
Formato: JSON
Autenticação: nenhuma
Município-alvo: BH tem código IBGE 3106200 — usado como filtro de localidade em qualquer consulta
Estabilidade: alta, API de referência nacional, também acessível via pacotes prontos em R (sidra, ibger) e Python (DadosAbertosBrasil)
API de Malhas (geometria): https://servicodados.ibge.gov.br/api/v2/malhas/{municipio}?formato=application/vnd.geo+json&resolucao=N — retorna a malha (contorno) do município em GeoJSON, permitindo cruzar diretamente com o BHGEO (após reprojeção)

### 4.5 PNCP — Portal Nacional de Contratações Públicas
Ambiente de produção: https://pncp.gov.br/api/consulta (consultas, sem autenticação) e https://pncp.gov.br/api/pncp (manutenção/gravação, com JWT)
Protocolo: REST/HTTP 1.1, JSON (charset ISO-8859-1 no cabeçalho da requisição, UTF-8 em arquivos)
Autenticação para consulta: nenhuma — o "acesso ao Portal de consultas é público"
Autenticação para inserção/alteração: login/senha (credenciamento junto ao órgão gestor) → token JWT com validade de 1 hora, obtido em POST /api/pncp/v1/usuarios/login
Endpoints de consulta relevantes (exemplos citados na documentação): consulta de contratações por data de publicação, consulta de atas de registro de preço por período de vigência ou por compra, consulta de contratações com período de recebimento de propostas em aberto
Filtro por órgão: por CNPJ do órgão/entidade — a PBH e suas empresas (PRODABEL, BHTRANS, SLU, SUDECAP, URBEL, PBH Ativos etc.) têm CNPJs próprios que podem ser usados como filtro
Documentação: Manual de Integração v2.5 (completo) + Swagger UI interativo
Potencial para dataspace: altíssimo, porque é a única fonte nacional que já obriga, por lei, todo o ciclo de compras públicas municipais a estar disponível em API estruturada — resolve de forma nativa a categoria "licitações/contratos/compras públicas" pedida no escopo do TCC

## 5. Análise para construção do dataspace

### 5.1 Interoperabilidade
Pontos fortes identificados:
Padrão CKAN duplicado entre PBH (dados.pbh.gov.br) e MG (dados.mg.gov.br) — mesma Action API, mesma estrutura de metadados (DCAT-like), o que reduz drasticamente o esforço de um conector genérico capaz de falar com ambos.
Código de município IBGE (3106200 para BH) aparece, ainda que de forma inconsistente, como possível chave de junção entre IBGE, SEJUSP/MG, SINESP, ANEEL e, potencialmente, datasets da PBH — mas isso precisa ser verificado empiricamente dataset a dataset na próxima etapa, pois não há garantia de que todos os publicadores incluam esse código de forma explícita e padronizada.
GTFS como padrão de fato internacional para mobilidade — facilita a futura comparação com outras cidades brasileiras que também publicam GTFS.
OGC WMS/WFS no BHGEO — padrão internacional de geoprocessamento, compatível com qualquer cliente GIS.
Problemas de incompatibilidade identificados:
SRID divergente: BHGEO usa EPSG:31983 (SIRGAS 2000 / UTM 23S); a maior parte das APIs nacionais (IBGE, INDE, GeoJSON "padrão web") usa EPSG:4326 (WGS84). Qualquer integração cruzando dado espacial municipal com dado espacial nacional exige uma camada de reprojeção — este é o problema de interoperabilidade técnica mais concreto encontrado no levantamento.
Ausência aparente de GTFS-Realtime: o dado de posição de ônibus em tempo real da BHTRANS não segue o padrão GTFS-RT (protobuf), e sim um formato próprio de coordenadas — reduz a interoperabilidade "out of the box" com ferramentas do ecossistema GTFS.
Heterogeneidade de nível de granularidade temporal: datasets variam de "tempo real" (ônibus) a "eventual"/"sob demanda" (ex.: heliportos) dentro do mesmo portal, exigindo que o catálogo do dataspace registre explicitamente a periodicidade esperada de cada fonte (o próprio CKAN da PBH já registra esse metadado como "Periodicidade prevista para publicação").
DATASUS/TabNet não expõe API REST tradicional — é uma ferramenta de tabulação web. Qualquer integração exigiria camada de scraping ou uso de pacotes de terceiros que já fazem esse trabalho (ex.: pacote R microdatasus), o que muda a categoria da fonte de "API oficial" para "acesso estruturado, mas sem API".
Vocabulários não controlados entre órgãos: por exemplo, "obras públicas" aparece tanto no Portal da Transparência (financeiro) quanto na SMOBI (execução) quanto no BHGEO (localização), sem um identificador único de "obra" compartilhado entre as três visões — isso é uma lacuna semântica real, não apenas técnica.

### 5.2 Metadados

| Fonte | O que são os dados | Quem produz | Quando foram atualizados | Granularidade | Como acessar | Restrições de uso |
|---|---|---|---|---|---|---|
| CKAN PBH | Sim (descrição textual por dataset) | Sim (organização/secretaria) | Sim (campo "periodicidade prevista") | Variável, geralmente explícita | Sim (URL/API documentada) | Licença por dataset (predominante CC-BY) |
| BHGEO/BHMAP | Sim (via GeoNetwork) | Sim (secretaria responsável pela camada) | Parcial (depende da camada) | Sim (SRID e escala documentados) | Sim (WMS/WFS + tutoriais) | A confirmar por camada |
| IBGE Agregados | Sim (endpoint /metadados dedicado) | Sim (pesquisa/IBGE) | Sim (endpoint /periodos) | Sim (nível geográfico explícito no endpoint) | Sim (documentação completa) | Uso público, citar fonte |
| PNCP | Sim (manual completo) | Sim (por CNPJ do órgão) | Sim (datas de publicação) | Sim (por processo/item) | Sim (Swagger) | Uso público |
| DATASUS/TabNet | Parcial (dicionários por sistema, dispersos) | Sim | Parcial | Sim, mas exige navegação manual | Não via API — apenas via portal tabulador | Uso público |
| Portal Transparência PBH | Parcial (glossário genérico, não por dataset) | Sim | Parcial | Variável | Via CKAN para exportação | A confirmar |

Conclusão da avaliação de metadados: as fontes construídas sobre CKAN (PBH, MG) e sobre padrões internacionais (IBGE, PNCP, OGC/BHGEO) têm metadados suficientes para descoberta automatizada. As fontes que dependem de portais de visualização/tabulação (DATASUS/TabNet, partes do Portal da Transparência) não oferecem essa mesma qualidade de metadado programático e exigiriam trabalho adicional de curadoria manual antes de entrar no catálogo do dataspace.

### 5.3 Arquitetura conceitual proposta
[Fonte de dados]                [API / Connector]            [Catálogo / Metadados]         [Camada de interoperabilidade]        [Consumidor]
CKAN PBH  ───────────────► Connector CKAN (genérico) ───►  Harvester DCAT  ───────►   Normalização de:                ───►   Aplicações,
CKAN MG   ───────────────► (mesmo connector, 2 instâncias)                             - código de município (IBGE)          dashboards,
- SRID (reprojeção p/ EPSG:4326)      pesquisa acadêmica,
BHGEO/BHMAP (WMS/WFS) ───► Connector OGC (GeoServer) ──►  Catálogo de camadas ────►   - vocabulário de categorias           protótipo do TCC
(reaproveita GeoNetwork          (mapeamento simples de-para)
já existente)
GTFS/Tempo-real BHTRANS ─► Connector de arquivo/polling ► Ficha de dataset ───────►   - normalização de timestamp/fuso
(BRT, UTC-3)
IBGE (Agregados/Malhas) ─► Connector REST nativo ──────►  Auto-descoberto via         - chave universal: código IBGE
endpoint /metadados            do município (3106200 = BH)
PNCP ────────────────────► Connector REST nativo ──────►  Auto-descoberto via Swagger  - chave: CNPJ do órgão/entidade
Princípio de design (recomendação arquitetural, não fato): seguindo a proposta explícita do enunciado do TCC, os dados devem permanecer na fonte sempre que a fonte já oferecer uma API estável e com boa disponibilidade (CKAN PBH/MG, IBGE, PNCP, BHGEO). A cópia para um repositório central só se justificaria para:
fontes sem API (ex.: TabNet), onde um pipeline de ETL periódico seria necessário de qualquer forma; ou
dados de "tempo real" de altíssima frequência (ex.: coordenadas de ônibus a cada 20s), onde manter um cache local de curto prazo evita sobrecarregar a fonte original a cada consulta do dataspace.
Isso é uma recomendação de arquitetura, a ser validada na etapa de implementação — não uma conclusão definitiva deste inventário.

### 5.4 Seleção de 3 a 5 fontes para o primeiro protótipo

| # | Fonte | Por que foi escolhida | Dado fornecido | Dificuldade de integração | Fontes relacionáveis | Papel no dataspace |
|---|---|---|---|---|---|---|
| 1 | CKAN da PBH (dados.pbh.gov.br) | API REST documentada, sem autenticação, cobre múltiplas categorias do escopo do TCC (finanças, mobilidade, meio ambiente, cultura), já é a fonte "âncora" natural do estudo de caso | Dezenas de datasets tabulares/geoespaciais | Baixa | Todas as demais (via código de município e por já hospedar BHTRANS/GTFS) | Fonte primária municipal generalista / prova de conceito do connector CKAN |
| 2 | BHGEO/BHMAP (WMS/WFS) | Único provedor de dado geoespacial estruturado e padronizado (OGC) já mantido pela própria PBH; permite demonstrar a integração de um padrão de interoperabilidade internacional (OGC) dentro do dataspace | Camadas de uso do solo, endereços, equipamentos urbanos | Média (exige lidar com SRID EPSG:31983 → reprojeção) | CKAN PBH (mesmas secretarias), IBGE Malhas (após reprojeção) | Fonte de referência espacial / demonstra problema real de interoperabilidade (SRID) e sua solução |
| 3 | GTFS + Tempo Real BHTRANS | Padrão internacional de mobilidade, dado dinâmico (bom para testar "consulta sob demanda" versus cópia), já citado em projeto de terceiros (Cadê Meu Busão) | Linhas, paradas, horários, posição de ônibus | Média (formato próprio para tempo real, não GTFS-RT) | CKAN PBH (mesma origem), BHGEO (malha viária) | Demonstra fonte de alta frequência de atualização e o trade-off cópia local vs. consulta direta |
| 4 | API de Agregados do IBGE (SIDRA) | API federal de altíssima qualidade técnica, documentação exemplar, permite trazer população/demografia como camada de contexto para qualquer outro dado municipal | População, indicadores socioeconômicos por município (BH = 3106200) | Baixa | Todas as fontes que citam código de município IBGE (MG, SINESP, ANEEL) | Fonte de enriquecimento nacional / demonstra escalabilidade do dataspace além de BH |
| 5 | PNCP — API de Consultas | Único caso do levantamento em que a interoperabilidade é imposta por lei (Lei 14.133/2021) a todos os entes federativos — ótimo argumento acadêmico de que o dataspace pode se apoiar em obrigações regulatórias já existentes | Licitações, contratos, atas de registro de preço da PBH e suas empresas (por CNPJ) | Baixa-média (API pública de consulta é simples; autenticação só é necessária para escrita, que não interessa ao protótipo) | CKAN PBH (dataset de licitações/contratos também existe lá, permitindo comparação), CNPJ das empresas municipais | Demonstra a categoria "compras públicas/licitações" pedida no escopo, com um provedor federal que abrange qualquer município do Brasil — melhor candidato para o "plano de evolução para escala nacional" |

Este conjunto de 5 fontes cobre, deliberadamente, quatro arquiteturas técnicas diferentes (CKAN, OGC/WMS-WFS, download/polling de arquivo, REST puro federal) — o que é mais valioso academicamente do que escolher 5 fontes fáceis, porque força o protótipo a implementar (ou ao menos desenhar) mais de um tipo de connector, demonstrando de forma mais robusta o conceito de dataspace.

## 6. Mapa das relações entre datasets (oportunidades de integração)

| Fonte A | Atributo/chave de ligação | Fonte B | Integração direta ou exige normalização? |
|---|---|---|---|
| GTFS/Tempo-real BHTRANS | stop_id / coordenada geográfica | BHGEO (malha viária, pontos de embarque) | Exige normalização de SRID (GTFS costuma usar WGS84; BHGEO usa EPSG:31983) |
| BHTRANS — Sinistros de trânsito (dataset CKAN) | Localização geográfica (endereço/coordenada) | BHGEO (malha viária) | Exige normalização de SRID + eventual geocodificação se o dado vier só como endereço textual |
| DATASUS/TabNet (saúde, agregado por município) | Código de município (IBGE) | IBGE Agregados (população) | Direta pelo código IBGE, mas exige ETL porque TabNet não tem API REST |
| SMED — dados de educação (CKAN PBH) | Código de município / possivelmente código INEP de escola | IBGE Agregados (população em idade escolar) | Direta pelo código de município; por escola, exigiria mapear para o Censo Escolar do INEP (fonte não aprofundada nesta etapa — lacuna) |
| SMOBI — obras públicas (CKAN PBH) | Localização (endereço/coordenada) | BHGEO | Exige normalização de SRID e possível geocodificação |
| Licitações/Contratos (CKAN PBH e/ou PNCP) | CNPJ do fornecedor/empresa | Empresas e atividades econômicas (fonte ainda não mapeada — ex. Receita Federal/CNPJ aberto) | Direta pelo CNPJ, mas a fonte de dados de empresas (ex. dados.gov.br CNPJ aberto da Receita Federal) não foi aprofundada nesta etapa — registrada como lacuna |
| SEJUSP/MG — crimes violentos por município | Código de município (IBGE) | IBGE Agregados (população, para taxas per capita) | Direta pelo código IBGE — bom candidato de "quick win" para o protótipo, pois ambas as fontes já usam o mesmo identificador |
| Meio ambiente (SMMA, CKAN PBH) | Localização geográfica | BHGEO | Exige normalização de SRID |
| Mobilidade (BHTRANS) | Horário/evento | Eventos/turismo (BELOTUR, CKAN PBH) | Não avaliado tecnicamente nesta etapa — relação conceitual plausível (ex. reforço de linhas em datas de Carnaval), mas exigiria cruzar calendário de eventos com GTFS — registrado como hipótese, não fato |


## 7. Principais problemas de interoperabilidade identificados
Divergência de sistema de referência espacial (SRID): BHGEO/BHMAP usa EPSG:31983; a maioria das fontes nacionais e o padrão web usam EPSG:4326. É o problema técnico mais concreto e mais fácil de resolver (reprojeção matemática padrão), mas precisa estar explícito na camada de interoperabilidade do dataspace.
Ausência de padrão GTFS-Realtime: o dado de posição de ônibus em tempo real não segue o padrão internacional GTFS-RT, o que impede reaproveitamento direto de bibliotecas/consumidores já preparados para esse padrão.
Falta de identificador único e compartilhado de "obra pública", "escola" ou "estabelecimento de saúde" entre as diferentes secretarias/fontes que tratam do mesmo objeto sob perspectivas diferentes (financeira, geográfica, operacional) — problema semântico, não meramente técnico.
Fontes sem API REST tradicional (TabNet/DATASUS) exigem camada de ETL/scraping controlado, o que foge do princípio de "dado permanece na fonte, acessado sob demanda" proposto no enunciado do TCC.
Ausência de rate limit documentado explicitamente em várias APIs municipais (CKAN da PBH menciona a existência de limite, mas não o valor) — isso é um risco operacional para o dataspace, que precisa de uma política de throttling defensiva mesmo sem saber o limite exato do provedor.
Heterogeneidade de licenças — a maior parte dos datasets do CKAN da PBH aparenta usar CC-BY, mas isso não foi confirmado dataset a dataset nesta etapa; outras fontes (ANEEL, IBGE, PNCP) têm políticas de uso público que precisam ser mapeadas uma a uma antes de qualquer redistribuição pelo dataspace.
Municípios da RMBH fora de BH têm portais heterogêneos (ou inexistentes) — isso não é um problema de BH em si, mas é a principal barreira identificada para o plano de expansão de Nível 1 → Nível 2 (RMBH) mencionado no enunciado.

## 8. Ranking das fontes mais adequadas
Critérios de pontuação (1–5 cada): relevância para BH; disponibilidade de API; qualidade da documentação; frequência de atualização; qualidade dos metadados; interoperabilidade; estabilidade; facilidade de integração; potencial de relacionamento; potencial para demonstrar o conceito de dataspace. Pontuação final = soma simples (máx. 50).
As notas abaixo são avaliações qualitativas do autor deste levantamento, baseadas nas evidências documentais coletadas — não são métricas fornecidas pelas próprias fontes.

| Fonte | Relevância BH | API | Doc. | Atualização | Metadados | Interop. | Estabilidade | Facilidade | Relacionamento | Potencial dataspace | Total (50) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CKAN da PBH | 5 | 5 | 4 | 3 | 4 | 4 | 5 | 5 | 5 | 5 | 45 |
| IBGE Agregados/SIDRA | 3 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 4 | 46 |
| BHGEO/BHMAP (WMS/WFS) | 5 | 4 | 3 | 3 | 4 | 3 | 4 | 3 | 4 | 5 | 38 |
| PNCP | 4 | 5 | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 5 | 44 |
| GTFS/Tempo-real BHTRANS | 5 | 3 | 3 | 5 | 3 | 3 | 4 | 3 | 4 | 4 | 37 |
| Portal de Dados Abertos MG (CKAN) | 4 | 5 | 4 | 3 | 4 | 5 | 4 | 4 | 4 | 4 | 41 |
| ANEEL Dados Abertos | 2 | 5 | 4 | 3 | 4 | 4 | 4 | 4 | 3 | 3 | 36 |
| INMET | 2 | 4 | 4 | 5 | 3 | 4 | 4 | 3 | 3 | 3 | 35 |
| Portal Transparência PBH | 4 | 2 | 3 | 3 | 2 | 2 | 4 | 2 | 3 | 2 | 27 |
| DATASUS/TabNet | 3 | 1 | 3 | 3 | 3 | 2 | 4 | 1 | 3 | 2 | 25 |
| SEJUSP/MG (REDS) | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 28 |
| Portal Transparência Federal (CGU) | 1 | 4 | 5 | 4 | 4 | 3 | 5 | 3 | 2 | 2 | 33 |
| SINESP nacional | 2 | 2 | 3 | 2 | 3 | 3 | 3 | 2 | 3 | 3 | 26 |
| OpenBHBus (terceiros) | 3 | 4 | 2 | 2 | 1 | 2 | 1 | 3 | 2 | 1 | 21 |
| CMBH Transparência | 3 | 1 | 1 | 1 | 1 | 1 | 3 | 1 | 1 | 1 | 14 |

Ranking final (top 5): CKAN PBH → IBGE Agregados → PNCP → Portal MG (CKAN) → BHGEO/BHMAP, com GTFS/Tempo-real BHTRANS logo em seguida — o que confirma e reforça a seleção do item 5.4.

## 9. Classificação A/B/C/D das fontes

### A. Fontes com API oficial documentada
CKAN da PBH (dados.pbh.gov.br)
BHGEO/BHMAP (WMS/WFS)
IBGE (Agregados/SIDRA, Localidades/Malhas)
PNCP (API de consulta)
Portal de Dados Abertos de MG (CKAN)
ANEEL Dados Abertos
INMET (API + BDMEP)
Portal da Transparência do Governo Federal (requer token)
dados.gov.br (Portal Brasileiro de Dados Abertos)

### B. Fontes com acesso estruturado, mas sem API própria
GTFS/Tempo-real BHTRANS (download recorrente, formato estruturado, mas não é "API de consulta" no sentido REST)
Portal da Transparência da PBH (a maior parte navegável em HTML; partes exportáveis via CKAN)
DATASUS/TabNet (tabulador web, exportação manual)
SEJUSP/MG — Armazém REDS (planilhas publicadas dentro do CKAN de MG)

### C. Fontes sem acesso estruturado (exigiriam scraping)
Câmara Municipal de BH — Portal de Transparência (aparentemente apenas HTML/PDF — não confirmado se há exportação estruturada)
Agência RMBH — Portal de Compras/Transparência (aparentemente apenas HTML/PDF)

### D. Fontes inadequadas para o protótipo nesta etapa
OpenBHBus (projeto de terceiros, não oficial, dependência de infraestrutura não institucional — Heroku de um desenvolvedor individual; risco de descontinuidade)
SINESP nacional em seu módulo operacional (acesso restrito a agentes de segurança, exige aprovação — o dataset aberto correlato em dados.mj.gov.br é utilizável, mas o sistema em si não)

## 10. Proposta de arquitetura inicial do dataspace
Ver diagrama completo na seção 5.3. Em resumo, a arquitetura conceitual recomendada segue o padrão:
Fonte de dados → API/Connector → Catálogo/Metadados → Camada de interoperabilidade → Consumidor
com três tipos de connector a serem prototipados:
Connector CKAN genérico (reutilizável para PBH e MG, e potencialmente para qualquer outro município/estado brasileiro que use CKAN — o que já demonstra, por si só, escalabilidade para o Nível 3/Brasil mencionado no enunciado);
Connector OGC (WMS/WFS) para BHGEO, com módulo de reprojeção de SRID;
Connector REST direto para IBGE e PNCP, ambos já nativamente JSON/REST e sem necessidade de adaptação de formato — apenas de normalização de chaves (código IBGE de município, CNPJ de órgão).
A camada de catálogo/metadados pode se inspirar diretamente no modelo do Catálogo de Dados Abertos (ECI/UFMG) citado no enunciado do TCC — ele já demonstra, em produção, como estruturar uma ficha por API (nome, órgão, endpoint, autenticação, formato) de forma reutilizável como inspiração de esquema de metadados do dataspace, ainda que ele mesmo não seja uma fonte de dados de BH.

## 11. Plano de evolução: BH → RMBH → Brasil
Fase atual (Nível 1 — BH): conectar CKAN PBH, BHGEO, GTFS/BHTRANS, IBGE e PNCP como protótipo, validando os 3 tipos de connector propostos.
Fase 2 (Nível 2 — RMBH): investigar, para cada um dos 33 demais municípios da RMBH, se existe portal de dados abertos e, principalmente, se ele usa CKAN (o que reaproveitaria diretamente o connector já construído) — esta investigação não foi feita nesta etapa e é uma lacuna explícita para a próxima.
Fase 3 (Nível 3 — Brasil): o connector CKAN genérico e os connectors REST para IBGE/PNCP já são, por natureza, nacionais — a escala para outras capitais seria primariamente um problema de descoberta de novas instâncias (outros dados.<uf>.gov.br ou dados.<municipio>.gov.br) e de enriquecimento do catálogo, não de reengenharia dos connectors. O Catálogo de Dados Abertos da ECI/UFMG e o próprio dados.gov.br são bons pontos de partida para essa descoberta automatizada na próxima etapa.

## 12. Lacunas que precisam ser investigadas na próxima etapa
Confirmar, dataset a dataset no CKAN da PBH, quais efetivamente trazem o código de município IBGE e/ou CNPJ como campo estruturado (não apenas em texto livre na descrição).
Verificar se o CKAN da PBH expõe o endpoint package_search (com paginação e filtros fq) além dos quatro endpoints documentados no guia de usuário consultado — este guia pode não ser exaustivo, e o software CKAN nativamente oferece mais endpoints do que os quatro citados.
Obter o valor exato do limite de taxa de requisições (rate limit) do CKAN da PBH e do BHGEO — mencionado como existente, mas sem valor publicado nas fontes consultadas.
Investigar se existe, de fato, alguma exposição de dados em GTFS-Realtime (protobuf) por parte da BHTRANS, ou se a Prefeitura tem plano de adotar esse padrão — não localizado nesta etapa.
Levantar a fonte de dados de empresas e CNPJs (ex. Receita Federal — Cadastro Nacional de Empresas aberto) para viabilizar a relação "licitações/compras → empresas" mencionada no escopo do TCC — não aprofundada nesta etapa.
Levantar fonte de dados imobiliários (ex. IPTU, cadastro imobiliário da PBH) — mencionada no escopo do TCC, mas não localizada com detalhe suficiente nesta etapa além da menção genérica a "distribuição imobiliária no território municipal" encontrada em um relatório do portal.
Confirmar existência (ou não) de API própria e estruturada no Portal de Transparência da CMBH (Câmara Municipal) e na Agência RMBH — marcadas como "Não confirmado" nesta etapa.
Levantar dados de educação a nível de escola (Censo Escolar/INEP, QEdu) para complementar os dados de SMED já presentes no CKAN da PBH — não aprofundado nesta etapa.
Confirmar as licenças exatas (CC-BY vs. outras) por dataset relevante antes de qualquer uso/redistribuição no protótipo.
Testar empiricamente (em ambiente controlado, sem sobrecarregar os servidores) ao menos uma requisição real a cada uma das 5 fontes selecionadas para o protótipo, documentando exemplos reais de request/response — não realizado nesta etapa por se tratar de um levantamento documental, conforme escopo definido ("Quando possível, forneça exemplos reais de requisições e respostas, sem executar operações que alterem dados" — a execução de leitura ficou reservada para a etapa de implementação).

## Fontes consultadas (documentação primária)
Portal de Dados Abertos da PBH — https://dados.pbh.gov.br/
CKAN da PBH — https://ckan.pbh.gov.br/
Guia de uso da API CKAN da PBH (Portal Data BH) — https://databh.pbh.gov.br/dados-abertos
Organizações do CKAN da PBH — https://dados.pbh.gov.br/organization/
BHGEO — Geoprocessamento na PBH — https://prefeitura.pbh.gov.br/bhgeo/geoprocessamento-pbh
Acesso aos Dados Geográficos (BHGEO) — https://prefeitura.pbh.gov.br/bhgeo/acesso-aos-dados
BHMap — Acesso Desktop (WMS/WFS) — https://bhmap.pbh.gov.br/v2/home.html
Institucional BHGEO (histórico INDE) — https://prefeitura.pbh.gov.br/bhgeo/institucional
Dataset GTFS/Tempo Real Ônibus — https://dados.pbh.gov.br/dataset/tempo_real_onibus_-_coordenada
BHTRANS GTFS no Mobility Database — https://mobilitydatabase.org/feeds/gtfs/mdb-9
Projeto "Cadê Meu Busão" — https://github.com/tarifazero/monitoramento
OpenBHBus (terceiros) — https://github.com/lucasparreiras/OpenBHBUs
Portal da Transparência da PBH — https://prefeitura.pbh.gov.br/transparencia
Plano de Dados Abertos da PRODABEL 2020-2021 — https://ckan.pbh.gov.br (relatório PDF)
Portal de Dados Abertos de Minas Gerais — https://dados.mg.gov.br/
SEJUSP/MG — Dados Abertos de Segurança Pública — https://www.seguranca.mg.gov.br/index.php/transparencia/dados-abertos
SINESP (dataset aberto) — https://dados.mj.gov.br/dataset/sistema-nacional-de-estatisticas-de-seguranca-publica
IBGE — API de Agregados — https://servicodados.ibge.gov.br/api/docs/agregados?versao=3
IBGE — Serviços de Dados (documentação geral) — https://servicodados.ibge.gov.br/api/docs/
INMET — Como acessar dados meteorológicos — https://portal.inmet.gov.br/noticias/saiba-como-acessar-os-dados-meteorol%C3%B3gicos-dispon%C3%ADveis-no-site-do-inmet
ANEEL — Portal de Dados Abertos — https://dadosabertos.aneel.gov.br/
PNCP — Manual de Integração v2.5 — https://pncp.gov.br/manual/pt-br/latest/singlehtml/
PNCP — Swagger de Consultas — https://pncp.gov.br/api/consulta/swagger-ui/index.html
Portal da Transparência do Governo Federal — API de Dados — https://portaldatransparencia.gov.br/api-de-dados
Portal Brasileiro de Dados Abertos — https://dados.gov.br/
Catálogo de Dados Abertos (ECI/UFMG) — https://catalogodedadosabertos.com.br/
Nota metodológica final: este documento é um inventário exploratório de Etapa 1, baseado em pesquisa documental. Ele não substitui testes empíricos de cada API (a serem feitos na etapa de implementação) e contém, de forma deliberada e explícita, itens marcados como "Não confirmado" onde a evidência disponível não permitiu uma afirmação segura — em nenhum ponto foram inventados endpoints, formatos ou políticas de acesso.
