# app/api/v1/endpoints/earnings.py
from fastapi import APIRouter
from src.adapters.outbound.neo4j.uow import Neo4jUnitOfWork
from src.adapters.outbound.logging.std_logger import StdLogger

from src.service_layer.update_supplier import UpdateSupplyChain
router = APIRouter()


def uow_factory() -> Neo4jUnitOfWork:
    return Neo4jUnitOfWork()

@router.post("/update_supplychain")
async def update_supplychain():
    service = UpdateSupplyChain(uow_factory=uow_factory,logger=StdLogger())
    result = await service.run()
    return result
