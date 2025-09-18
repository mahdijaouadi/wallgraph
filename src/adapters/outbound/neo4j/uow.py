from neo4j import AsyncSession
from src.adapters.outbound.neo4j.driver import get_admin_session
from src.adapters.outbound.neo4j.ticker_repository import Neo4jTickerRepository
from src.adapters.outbound.neo4j.earnings_repository import Neo4jEarningsRepository

class Neo4jUnitOfWork:
    def __init__(self) -> None:
        self._session: AsyncSession | None = None
        self._tx = None
        self.ticker_repository = None
        self.earnings_repository = None
        self._committed = False

    async def __aenter__(self):
        self._session = await get_admin_session()
        self._tx = await self._session.begin_transaction()

        # Bind both repos to the SAME tx
        self.ticker_repository = Neo4jTickerRepository(self._tx)
        self.earnings_repository = Neo4jEarningsRepository(self._tx)

        self._committed = False
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type or not self._committed:
                await self._tx.rollback()
        finally:
            await self._session.close()

    async def commit(self):
        await self._tx.commit()
        self._committed = True

    async def rollback(self):
        await self._tx.rollback()
