from src.domain.ports import FinancialsProvider
from src.domain.models import Ticker, Financials
import yfinance as yf
from datetime import datetime
import pandas as pd


class YfinanceFinancialProvider(FinancialsProvider):
    async def get_financials(self, ticker: Ticker) -> Financials:
        yf_ticker = yf.Ticker(ticker.ticker_name)
        financials=yf_ticker.quarterly_financials
        latest_col = max(pd.to_datetime(financials.columns))
        latest_date = latest_col.strftime("%Y-%m-%d")
        latest_values = financials[latest_date] 
        financials=latest_values.to_dict()
        financials["date"]=latest_date

        return Financials(financials_id="*",
                        date=financials["date"],
                        total_revenue=financials.get("Total Revenue", 0.0),
                        gross_profit=financials.get("Gross Profit", 0.0),
                        operating_income=financials.get("Operating Income", 0.0),
                        net_income=financials.get("Net Income", 0.0),
                        ebitda=financials.get("EBITDA", 0.0),
                        diluted_eps=financials.get("Diluted EPS", 0.0),
                        basic_avg_shares=financials.get("Basic Average Shares", 0.0),
                        diluted_avg_shares=financials.get("Diluted Average Shares", 0.0),
                        tax_provision=financials.get("Tax Provision", 0.0))


