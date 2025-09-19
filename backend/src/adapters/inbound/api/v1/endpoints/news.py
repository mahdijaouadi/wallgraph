# app/api/v1/endpoints/earnings.py
from fastapi import APIRouter
from backend.src.adapters.outbound.logging.std_logger import StdLogger

from backend.src.service_layer.update_news import UpdateNews
from backend.src.adapters.outbound.neo4j import Neo4jUnitOfWork

router = APIRouter()


def uow_factory():
    return Neo4jUnitOfWork()

@router.post("/update_news")
async def update_news():
    service = UpdateNews(uow_factory=uow_factory,logger=StdLogger())
    result = await service.run()
    return result
