import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Diretório e arquivo de log (podem ser sobrescritos por variáveis de ambiente)
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "b3_scraper.log")
# Tamanho máximo de 10MB e até 5 arquivos de backup por padrão
MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))
BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))


def configure_logging(level: str = None):
    """
    Configura o logger root com handlers de console e arquivo.
    :param level: nível de log (ex.: 'DEBUG', 'INFO'). Se None, lê de LOG_LEVEL.
    """
    level = level or os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Garante existência do diretório de logs
    os.makedirs(LOG_DIR, exist_ok=True)

    # Configura o logger root
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Formato padrão para todos os handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler rotativo para arquivo
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)