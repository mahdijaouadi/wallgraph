import imp
from backend.src.domain.ports import TickerRepository
from typing import Iterable, Optional, List
from backend.src.domain.models import Ticker, Earnings
from backend.src.adapters.outbound.neo4j.driver import get_admin_session
from backend.src.adapters.outbound.neo4j.common_queries import create_node,add_relation
from neo4j import AsyncTransaction



class Neo4jTickerRepository(TickerRepository):
    def __init__(self,tx: AsyncTransaction) -> None:
        self.tx=tx
    async def get_all_tickers(self) -> List[Ticker]:
        query = """
        MATCH (ticker:TICKER)
        RETURN ticker.id AS ticker_id, ticker.ticker_name AS ticker_name, ticker.founded AS founded
        """
        result = await self.tx.run(query)
        records = await result.data()
        return [Ticker(**record) for record in records]

    async def add_ticker(self,ticker: Ticker) -> str:
        await create_node(tx=self.tx,label="TICKER",properties=ticker)
