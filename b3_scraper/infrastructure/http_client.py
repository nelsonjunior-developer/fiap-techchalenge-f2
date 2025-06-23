

"""
b3_scraper.infrastructure.http_client
Cliente HTTP com retry/backoff para requisições ao site da B3.
"""
import logging
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class HttpClient:
    """
    Wrapper em torno de requests.Session que adiciona retry/backoff.
    """
    def __init__(
        self,
        timeout: int,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: Optional[frozenset] = frozenset({500, 502, 503, 504})
    ):
        """
        :param timeout: tempo máximo de espera para cada requisição (em segundos)
        :param max_retries: número máximo de tentativas em caso de falha
        :param backoff_factor: fator de backoff exponencial entre tentativas
        :param status_forcelist: códigos HTTP que disparam retry
        """
        self.timeout = timeout
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods={"GET", "POST"}
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Executa um GET e retorna o conteúdo de resposta como texto.
        """
        logger.debug("HttpClient GET url=%s params=%s headers=%s", url, params, headers)
        response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Executa um POST e retorna o conteúdo de resposta como texto.
        """
        logger.debug("HttpClient POST url=%s data=%s json=%s headers=%s", url, data, json, headers)
        response = self.session.post(url, data=data, json=json, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text