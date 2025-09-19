from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import settings
from src.adapters.outbound.neo4j.driver  import init_driver, close_driver
from src.adapters.inbound.api.v1.router import api_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from src.config.logging import setup_logging


setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_driver()
    yield
    await close_driver()
current_dir = os.path.dirname(os.path.abspath(__file__))
# frontend_dir = os.path.abspath(os.path.join(current_dir, "../../frontend"))
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# @app.get("/")
# async def root():
#     index_path = os.path.join(frontend_dir, "index.html")
#     return FileResponse(index_path)

@app.get("/health", tags=["health"])  # simple liveness probe
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})

app.include_router(api_router, prefix=settings.api_v1_prefix) 