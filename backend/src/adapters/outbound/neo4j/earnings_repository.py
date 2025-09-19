from dataclasses import asdict, replace
from backend.src.domain.ports import EarningsRepository
from backend.src.domain.models import Ticker, Earnings
from backend.src.adapters.outbound.neo4j.common_queries import create_node, add_relation
from neo4j import AsyncTransaction

class Neo4jEarningsRepository(EarningsRepository):
    def __init__(self, tx: AsyncTransaction) -> None:
        self.tx = tx

    async def add_earnings(self, earnings: Earnings) -> Earnings:
        props = asdict(earnings)
        props.pop("earnings_id", None)
        props["earnings_id"] = await create_node(tx=self.tx, label="EARNINGS", properties=props)
        return Earnings(**props)
    
    async def link_earnings_to_ticker(self,ticker: Ticker, earnings: Earnings ) -> str:
        await add_relation(tx=self.tx,
                        left_label="TICKER",
                        right_label="EARNINGS",
                        rel_label="HAS_EARNINGS",
                        left_id=ticker.ticker_id,
                        right_id=earnings.earnings_id,
                        properties={})
        return "HAS_EARNINGS relation added successfully"
    
    async def check_earnings_existence(self, earnings: Earnings, ticker: Ticker) -> bool:
        query = """
        MATCH (ticker:TICKER)-[:HAS_EARNINGS]->(earnings:EARNINGS)
        WHERE earnings.date = $date AND ticker.ticker_name = $ticker_name
        RETURN earnings.date AS earnings_date
        """
        result = await self.tx.run(query, {"date": earnings.date, "ticker_name":ticker.ticker_name})
        record = await result.single()

        if record:
            return True
        else:
            return False

