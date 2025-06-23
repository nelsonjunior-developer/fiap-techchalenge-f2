"""
b3_scraper.application.orchestrator
Orquestra o fluxo principal: fetch -> parse -> store.
"""
import logging
import json

from b3_scraper.config import settings
from b3_scraper.infrastructure.http_client import HttpClient
from b3_scraper.infrastructure.scraper import Scraper
from b3_scraper.infrastructure.parser import Parser
from b3_scraper.infrastructure.storage import Storage
from b3_scraper.logger import configure_logging

import pandas as pd
from datetime import datetime, date

# Configura logging antes de tudo
configure_logging()

logger = logging.getLogger(__name__)

def run():
    """
    Executa o fluxo de scraping:
    1. Busca o JSON do pregão IBOV.
    2. Converte o JSON em registros de negócio.
    3. Persiste os registros no S3.
    """
    # Cria cliente HTTP configurado
    http_client = HttpClient(timeout=settings.TIMEOUT)
    # Inicializa o scraper com URL base e path
    scraper = Scraper(
        http_client=http_client,
        base_url=settings.B3_BASE_URL,
        path=settings.IBOV_PATH,
    )
    # Faz o fetch do JSON
    data = scraper.fetch_json(page_number=1, page_size=settings.PAGE_SIZE)
    logger.debug("JSON fetched successfully")
    logger.debug("JSON payload: %s", data)

    # Parseia o JSON em registros de negócio
    parser = Parser()
    records = parser.parse_json(data)
    logger.info("Parsed %d records from JSON", len(records))
    # Log do conteúdo que será salvo no S3
    payload = [record.__dict__ for record in records]
    # Convert to DataFrame
    # Skip local write; directly upload to S3
    df = pd.DataFrame.from_records(payload)

    logger.debug("S3 payload: %s", payload)

    # Persiste os registros no S3
    storage = Storage(
        bucket=settings.S3_BUCKET,
        region=settings.AWS_REGION,
        prefix=settings.S3_PREFIX,
    )
    storage.save_records(records)
    logger.info("Saved %d records to S3://%s/%s", len(records), settings.S3_BUCKET, settings.S3_PREFIX)

if __name__ == "__main__":
    # Executa quando invocado diretamente
    run()