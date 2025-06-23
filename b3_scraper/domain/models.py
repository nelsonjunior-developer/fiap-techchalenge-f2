"""
b3_scraper.domain.models
Modelos de domínio para o scraper da B3.
"""
from dataclasses import dataclass
from decimal import Decimal
from datetime import date


@dataclass
class TradeRecord:
    """
    Representa um registro de negociação do IBOV:
    - code: Código de negociação (ticker)
    - stock: Nome da ação
    - type: Tipo do ativo
    - theoretical_quantity: Quantidade Teórica (Qtde. Teórica)
    - participation_percentage: Participação em % (Part. (%))
    - record_date: Data do pregão (DD/MM/YY)
    """
    code: str
    stock: str
    type: str
    theoretical_quantity: Decimal
    participation_percentage: Decimal
    record_date: date  # Data do pregão (DD/MM/YY)