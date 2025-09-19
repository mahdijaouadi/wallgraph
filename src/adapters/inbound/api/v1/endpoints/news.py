# app/api/v1/endpoints/earnings.py
from fastapi import APIRouter
from src.adapters.outbound.neo4j.uow import Neo4jUnitOfWork
from src.adapters.outbound.logging.std_logger import StdLogger

from src.service_layer.update_news import UpdateNews
router = APIRouter()


def uow_factory():
    return Neo4jUnitOfWork()

@router.post("/update_news")
async def update_news():
    service = UpdateNews(uow_factory=uow_factory,logger=StdLogger())
    result = await service.run()
    return result
