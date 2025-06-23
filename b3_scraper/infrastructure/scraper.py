

"""
b3_scraper.infrastructure.scraper
Classe responsável por baixar o HTML do pregão IBOV da B3.
"""
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import json
import base64
from b3_scraper.config import settings

from b3_scraper.infrastructure.http_client import HttpClient

logger = logging.getLogger(__name__)

class Scraper:
    """
    Orquestra as chamadas HTTP para baixar páginas do site da B3.
    """
    def __init__(
        self,
        http_client: HttpClient,
        base_url: str,
        path: str,
        default_params: Optional[Dict[str, Any]] = None,
    ):
        """
        :param http_client: instância de HttpClient para fazer as requisições
        :param base_url: URL base do site (ex: https://sistemaswebb3-listados.b3.com.br)
        :param path: caminho relativo à base_url (ex: /indexPage/day/IBOV)
        :param default_params: parâmetros de query padrão (ex: language)
        """
        self.http_client = http_client
        self.base_url = base_url
        self.path = path
        self.default_params = default_params or {"language": "pt-br"}

    def fetch(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Faz o fetch do HTML da página especificada.
        :param params: parâmetros de query adicionais que sobrescrevem os padrões
        :return: conteúdo HTML como string
        """
        merged_params = {**self.default_params, **(params or {})}
        url = urljoin(self.base_url, self.path)
        logger.info("Fetching URL %s with params %s", url, merged_params)
        html = self.http_client.get(url, params=merged_params)
        logger.debug("Fetched %d characters", len(html))
        return html

    def fetch_json(self, page_number: int = 1, page_size: int = None) -> dict:
        """
        Faz o fetch do endpoint JSON do pregão IBOV.
        """
        payload_dict = {
            "language": "pt-br",
            "pageNumber": page_number,
            "pageSize": page_size or settings.PAGE_SIZE,
            "index": settings.INDEX,
            "segment": settings.SEGMENT,
        }
        payload = json.dumps(payload_dict)
        encoded = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
        url = urljoin(self.base_url, f"indexProxy/indexCall/GetPortfolioDay/{encoded}")
        logger.info("Fetching JSON URL %s", url)
        response_text = self.http_client.get(url)
        return json.loads(response_text)