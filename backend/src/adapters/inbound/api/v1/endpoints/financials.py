# app/api/v1/endpoints/earnings.py
from fastapi import APIRouter
from backend.src.adapters.outbound.logging.std_logger import StdLogger

from backend.src.adapters.outbound.yfinance.financials_provider import YfinanceFinancialProvider
from backend.src.service_layer.update_financials import UpdateFinancials
from backend.src.adapters.outbound.neo4j import Neo4jUnitOfWork

router = APIRouter()


def uow_factory():
    return Neo4jUnitOfWork()

@router.post("/update_financials")
async def update_financials():
    service = UpdateFinancials(uow_factory=uow_factory, financials_provider=YfinanceFinancialProvider(),logger=StdLogger())
    result = await service.run()
    return result
