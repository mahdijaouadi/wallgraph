from dataclasses import asdict
from src.domain.ports import FinancialRepository
from src.domain.models import Ticker, Financials
from src.adapters.outbound.neo4j.common_queries import create_node, add_relation
from neo4j import AsyncTransaction

class Neo4jFinancialsRepository(FinancialRepository):
    def __init__(self, tx: AsyncTransaction) -> None:
        self.tx = tx

    async def add_financials(self, financials: Financials) -> Financials:
        props = asdict(financials)
        props.pop("financials_id", None)
        props["financials_id"] = await create_node(tx=self.tx, label="FINANCIALS", properties=props)
        return Financials(**props)
    
    async def link_financials_to_ticker(self,ticker: Ticker, financials: Financials ) -> str:
        await add_relation(tx=self.tx,
                        left_label="TICKER",
                        right_label="FINANCIALS",
                        rel_label="HAS_FINANCIALS",
                        left_id=ticker.ticker_id,
                        right_id=financials.financials_id,
                        properties={})
        return "HAS_FINANCIALS relation added successfully"
    
    async def check_financials_existence(self, financials: Financials, ticker: Ticker) -> bool:
        query = """
        MATCH (ticker:TICKER)-[:HAS_FINANCIALS]->(financials:FINANCIALS)
        WHERE financials.date = $date AND ticker.ticker_name = $ticker_name
        RETURN financials.date AS financials_date
        """
        result = await self.tx.run(query, {"date": financials.date, "ticker_name":ticker.ticker_name})
        record = await result.single()

        if record:
            return True
        else:
            return False

