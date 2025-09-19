# app/api/v1/endpoints/earnings.py
from fastapi import APIRouter
from src.adapters.outbound.neo4j.uow import Neo4jUnitOfWork
from src.adapters.outbound.logging.std_logger import StdLogger

from src.adapters.outbound.yfinance.financials_provider import YfinanceFinancialProvider
from src.service_layer.update_financials import UpdateFinancials
router = APIRouter()


def uow_factory():
    return Neo4jUnitOfWork()

@router.post("/update_financials")
async def update_financials():
    service = UpdateFinancials(uow_factory=uow_factory, financials_provider=YfinanceFinancialProvider(),logger=StdLogger())
    result = await service.run()
    return result
