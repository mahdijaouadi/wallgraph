# app/api/v1/endpoints/earnings.py
from fastapi import APIRouter
from backend.src.adapters.outbound.logging.std_logger import StdLogger

from backend.src.adapters.outbound.yfinance.earnings_provider import YfinanceEarningsProvider
from backend.src.service_layer.update_earnings import UpdateEarnings
from backend.src.adapters.outbound.neo4j import Neo4jUnitOfWork
router = APIRouter()


def uow_factory():
    return Neo4jUnitOfWork()

@router.post("/update_earnings")
async def update_earnings():
    service = UpdateEarnings(uow_factory=uow_factory, earnings_provider=YfinanceEarningsProvider(),logger=StdLogger())
    result = await service.run()
    return result
