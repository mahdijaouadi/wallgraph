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
    eps_estimate: float
    reported_eps: float
    surprise_percentage: float


@dataclass(frozen=True)
class Financials:
    financials_id: str
    date: str
    total_revenue: float                     
    gross_profit: float                
    operating_income: float        
    net_income: float      
    ebitda: float                         
    diluted_eps: float                        
    basic_avg_shares: float                  
    diluted_avg_shares: float                
    tax_provision: float


@dataclass(frozen=True)
class News:
    news_id: str
    date: str
    feed: float

@dataclass
class NewsSentiment:
    ticker: str
    sentiment: str
    justification: str


@dataclass
class TickerSupplierRelationship:
    supplier_id: str
    date: str
    supplier_name: str
    supplier_type: str
    relationship_type: str
    risk: str
    confidence_score: float
    evidence: str      
