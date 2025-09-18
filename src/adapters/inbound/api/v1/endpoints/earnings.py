# app/api/v1/endpoints/earnings.py
from fastapi import APIRouter
from src.adapters.outbound.neo4j.uow import Neo4jUnitOfWork
from src.adapters.outbound.yfinance.earnings_provider import YfinanceEarningsProvider
from src.service_layer.update_earnings import UpdateEarnings
router = APIRouter()

@router.post("/update_earnings")
async def update_earnings():
    service = UpdateEarnings(uow_factory=Neo4jUnitOfWork(), earnings_provider=YfinanceEarningsProvider())
    result = await service.run()
    return result
