from fastapi import APIRouter
from backend.src.adapters.inbound.api.v1.endpoints import earnings,financials, news, supplychain, agents


api_router = APIRouter()
# api_router.include_router(ticker.router, prefix="/ticker", tags=["ticker"])
api_router.include_router(earnings.router, prefix="/earnings", tags=["earnings"])
api_router.include_router(financials.router, prefix="/financials", tags=["financials"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(supplychain.router, prefix="/supplychain", tags=["supplychain"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])


