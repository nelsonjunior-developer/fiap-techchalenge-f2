# fiap-techchalenge-f2
 Aplicacacao que faz o scrap de dados do site da B3 com dados do pregão

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