"""
b3_scraper.infrastructure.parser
Parser que converte HTML bruto do IBOV em objetos TradeRecord.
"""
import logging
from typing import List
from decimal import Decimal
from datetime import datetime

from bs4 import BeautifulSoup

from b3_scraper.domain.models import TradeRecord

logger = logging.getLogger(__name__)

class Parser:
    """
    Converte HTML de tabela IBOV em uma lista de TradeRecord.
    """
    def parse(self, html: str) -> List[TradeRecord]:
        """
        :param html: conteúdo HTML da página IBOV
        :return: lista de TradeRecord extraídos do HTML
        """
        soup = BeautifulSoup(html, "html.parser")

        # Extrai a data do cabeçalho (formato "Carteira do Dia - DD/MM/YY")
        header_tag = soup.find("h2")
        if header_tag:
            full_text = header_tag.get_text(strip=True)
            date_str = full_text.split("-")[-1].strip()
            try:
                record_date = datetime.strptime(date_str, "%d/%m/%y").date()
            except ValueError:
                logger.warning("Formato de data inesperado no HTML: %s", full_text)
                record_date = None
        else:
            record_date = None

        table = soup.find("table")
        if not table:
            logger.error("Nenhuma tabela encontrada no HTML")
            return []

        # Cabeçalhos para mapear colunas
        thead = table.find("thead")
        if not thead:
            logger.error("Tabela sem <thead>")
            return []
        headers = [th.get_text(strip=True) for th in thead.find_all("th")]

        try:
            idx_code = headers.index("Código")
            idx_stock = headers.index("Ação")
            idx_type = headers.index("Tipo")
            idx_qty = headers.index("Qtde. Teórica")
            idx_part = headers.index("Part. (%)")
        except ValueError as e:
            logger.error("Cabeçalhos esperados não encontrados: %s", e)
            return []

        records: List[TradeRecord] = []
        for row in table.find("tbody").find_all("tr"):
            cells = row.find_all("td")
            # Extrai valores das células
            code = cells[idx_code].get_text(strip=True)
            stock = cells[idx_stock].get_text(strip=True)
            type_ = cells[idx_type].get_text(strip=True)
            # Normaliza e converte números: de "1.234,56" para Decimal("1234.56")
            qty_text = cells[idx_qty].get_text(strip=True).replace(".", "").replace(",", ".")
            part_text = cells[idx_part].get_text(strip=True).replace("%", "").replace(".", "").replace(",", ".")
            try:
                theoretical_quantity = Decimal(qty_text)
                participation_percentage = Decimal(part_text)
            except Exception as e:
                logger.warning("Erro ao converter numérico em linha: %s – %s", row, e)
                continue

            record = TradeRecord(
                code=code,
                stock=stock,
                type=type_,
                theoretical_quantity=theoretical_quantity,
                participation_percentage=participation_percentage,
                record_date=record_date,
            )
            records.append(record)

        return records


    def parse_json(self, data: dict) -> List[TradeRecord]:
        """
        Converte resposta JSON do IBOV em lista de TradeRecord.
        """
        # Extrai a data do pregão do JSON (formato "DD/MM/YY")
        date_str = data.get("header", {}).get("date", "").strip()
        try:
            record_date = datetime.strptime(date_str, "%d/%m/%y").date()
        except ValueError:
            logger.warning("Formato de data inesperado no JSON: %s", date_str)
            record_date = None

        records: List[TradeRecord] = []
        for item in data.get("results", []):
            code = item.get("cod", "").strip()
            stock = item.get("asset", "").strip()
            type_ = item.get("type", "").strip()
            # Normaliza e converte números para Decimal
            qty_text = item.get("theoricalQty", "").replace(".", "").replace(",", ".")
            part_text = item.get("part", "").replace(".", "").replace(",", ".")
            try:
                theoretical_quantity = Decimal(qty_text)
                participation_percentage = Decimal(part_text)
            except Exception:
                logger.warning("Erro ao converter números no JSON: %s", item)
                continue
            records.append(
                TradeRecord(
                    code=code,
                    stock=stock,
                    type=type_,
                    theoretical_quantity=theoretical_quantity,
                    participation_percentage=participation_percentage,
                    record_date=record_date,
                )
            )
        return records