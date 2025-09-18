from fastapi import APIRouter

# from backend.app.api.v1.endpoints import nodes, embeddings, gds, search
from src.adapters.inbound.api.v1.endpoints import earnings


api_router = APIRouter()
# api_router.include_router(ticker.router, prefix="/ticker", tags=["ticker"])
api_router.include_router(earnings.router, prefix="/earnings", tags=["earnings"])
