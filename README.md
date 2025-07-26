# fiap-techchalenge-f2
 Aplicacacao que faz o scrap de dados do site da B3 com dados do pregão

 ---

## Visão geral do scraper (`b3_scraper`)

O módulo **b3_scraper** automatiza o download diário da *Carteira do Dia* do índice **IBovespa** no site da B3 e a transforma em dados estruturados:

1. **Coleta**  
   `scraper.py` usa `http_client.py` (requests + retry) para buscar a página HTML; o artefato bruto pode ser salvo localmente ou diretamente no Amazon S3 (via `storage.py`) para auditoria/reprocessamento.

2. **Parsing.**  
   `parser.py` extrai a tabela do pregão (código do papel, nome, tipo, quantidade teórica, participação %) e converte cada linha em objetos `TradeRecord` (ver `domain/models.py`).

3. **Persistência estruturada.**  
   Os registros estruturados são serializados em **Parquet** e gravados em S3 em `s3://fiap-b3-rawdata/raw/ibov/YYYY/MM/DD/run-.parquet`

Esse particionamento por *ano/mês/dia* é fundamental para custo otimizado de leitura na etapa de analytics.

4. **Orquestração.**  
`application/orchestrator.py` amarra o fluxo *fetch → parse → store* e pode ser executado pelo CLI (`interfaces/cli.py`) ou por contêiner/cron.

---

## Objetivos do projeto na AWS 

> **Escopo entregue:** ingestão & processamento batch completo até consultas ad-hoc no **Athena**.

| Etapa | Serviço AWS | O que acontece? |
|-------|-------------|-----------------|
| **Ingestão raw** | **S3** | O scraper grava os Parquets brutos em `raw/ibov/YYYY/MM/DD/`. |
| **Disparo de processamento** | **Lambda (S3 trigger)** | Quando um novo arquivo chega, a Lambda aciona o job Glue visual `bovespa_refined_visual`. |
| **Transformação (camada _refined_)** | **AWS Glue Studio – modo visual** | <br>① **Agrupamento/contagem** por *ação* e *data*.<br>② **Renomeia** colunas (`stock → acao`, `code → code`, …).<br>③ Calcula **métricas de data** (`days_since_record`, `record_year`, `record_month`).<br><br>O resultado é salvo em Parquet, particionado por `record_date` e `acao_partition`, em `s3://fiap-b3-rawdata/refined/`. |
| **Catálogo** | **Glue Data Catalog** | O job cria/atualiza a tabela `default.bovespa_refined` apontando para a pasta *refined*. |
| **Consulta ad-hoc** | **Amazon Athena** | É possível executar SQL diretamente sobre `default.bovespa_refined`, por exemplo:<br>`SELECT * FROM default.bovespa_refined WHERE record_date='2025-07-21' ORDER BY acao;` |


## 🏗️ Estrutura do Projeto
```
FIAP-TECHCHALENGE-F2/
├── README.md
├── requirements.txt        # dependências do projeto
├── .env.default           # defaults e placeholders para as configuracoes
├── .gitignore
│
├── b3_scraper/             # pacote principal
│   ├── __init__.py
│   ├── config.py           # carregamento de settings via pydantic
│   ├── logger.py           # configuração de logging (rotacionamento, níveis)
│   │
│   ├── domain/             # modelos de negócio
│   │   ├── __init__.py
│   │   └── models.py       # dataclasses: TradeRecord, MarketSummary etc.
│   │
│   ├── infrastructure/     # “externals”: HTTP, parsing, storage
│   │   ├── __init__.py
│   │   ├── http_client.py  # wrapper requests.Session + retry/backoff
│   │   ├── scraper.py      # orquestra fetch de página(s)
│   │   ├── parser.py       # BeautifulSoup → domain.models
│   │   └── storage.py      # salvar raw HTML / JSON / CSV (local ou S3)
│   │
│   ├── application/        # casos de uso
│   │   ├── __init__.py
│   │   └── orchestrator.py # fluxo: fetch → parse → store
│   │
│   └── interfaces/         # entry-points
│       ├── __init__.py
│       └── cli.py          # argparse para invocar o scraper
│
└── tests/                  # unitários e de integração
    ├── __init__.py
    ├── test_http_client.py
    ├── test_parser.py
    ├── test_orchestrator.py
    └── test_storage.py
```







---

## 🛠️ Ambiente local & execução

Siga estes passos para preparar um ambiente **Python 3.9 +** e executar o scraper manualmente:

1. **Clone** o repositório (ou baixe o ZIP).  
   ```bash
   git clone https://github.com/nelsonjunior-developer/fiap-techchalenge-f2.git

   cd fiap-techchalenge-f2
   ```

2. **Crie** e **ative** um ambiente virtual:  
   ```bash
   python -m venv .venv
   # Linux / macOS
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

3. **Instale** as dependências:  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. (Opcional) **Configure variáveis** de ambiente copiando o template:  
   ```bash
   cp .env.default .env
   # edite .env se precisar alterar chaves / paths
   ```

5. **Execute** o scraper com logging detalhado:  
   ```bash
   python -m b3_scraper.interfaces.cli --verbose
   ```

Se tudo estiver correto, o script fará o download da *Carteira do Dia*, parseará os dados e gravará um arquivo Parquet na pasta `raw/` (ou diretamente no S3, dependendo das suas variáveis de ambiente).