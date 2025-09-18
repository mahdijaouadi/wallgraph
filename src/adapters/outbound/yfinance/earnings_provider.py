from src.domain.ports import EarningsProvider
from src.domain.models import Ticker, Earnings
import yfinance as yf
from datetime import datetime



class YfinanceEarningsProvider(EarningsProvider):
    async def get_earnings(self, ticker: Ticker) -> Earnings:
        yf_ticker = yf.Ticker(ticker.ticker_name)
        earnings=yf_ticker.earnings_dates.reset_index(drop=False)
        earnings["Earnings Date"]=earnings["Earnings Date"].astype(str) 
        earnings=earnings.iloc[0].to_dict()
        earnings["date"]=earnings.pop("Earnings Date",None)
        earnings["date"] = datetime.fromisoformat(earnings["date"])
        earnings["date"] = earnings["date"].strftime("%Y-%m-%d")
        return Earnings(earnings_id="*",date=earnings["date"],eps_estimate=earnings["EPS Estimate"],reported_eps=earnings["Reported EPS"],surprise_percentage=earnings["Surprise(%)"])


