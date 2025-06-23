from dotenv import load_dotenv
load_dotenv()

"""
b3_scraper.interfaces.cli
Interface de linha de comando para executar o scraper da B3 (IBOV).
"""
import argparse
import logging
import sys

from b3_scraper.logger import configure_logging
from b3_scraper.config import settings
from b3_scraper.application.orchestrator import run

def main():
    parser = argparse.ArgumentParser(
        description="Scraper de dados do pregão da B3 (IBOV)."
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Ativa logging em nível DEBUG."
    )
    parser.add_argument(
        "--page-size", type=int, default=settings.PAGE_SIZE,
        help="Número de registros por página (default: %(default)s)."
    )
    parser.add_argument(
        "--index", type=str, default=settings.INDEX,
        help="Índice para consulta (default: %(default)s)."
    )
    parser.add_argument(
        "--segment", type=str, default=settings.SEGMENT,
        help="Segmento de mercado (default: %(default)s)."
    )
    args = parser.parse_args()

    # Configura logging
    if args.verbose:
        configure_logging(level="DEBUG")
    else:
        configure_logging()

    # Sobrescreve configurações se fornecidas via CLI
    settings.PAGE_SIZE = args.page_size
    settings.INDEX = args.index
    settings.SEGMENT = args.segment

    try:
        run()
    except Exception as e:
        logging.getLogger().error("Falha na execução: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()