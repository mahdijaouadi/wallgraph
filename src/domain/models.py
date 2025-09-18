# app/domain/models.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class Ticker:
    ticker_id: str       
    ticker_name: str
    founded: str

@dataclass(frozen=True)
class Earnings:
    earnings_id: str
    date: str
    eps_estimate: int
    reported_eps: float
    surprise_percentage: float
