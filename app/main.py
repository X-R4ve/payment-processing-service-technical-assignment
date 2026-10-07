from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.versions.v1 import payment_processing_service_app_v1
from app.infrastructure.db.core.connection import DatabaseConnection
from app.infrastructure.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_connection = DatabaseConnection(db_url=get_settings().db.url)
    try:
        yield {'db_connection': db_connection}
    finally:
        await db_connection.close()

payment_processing_service_app = FastAPI(lifespan=lifespan)

payment_processing_service_app.mount(
    '/api/v1',
    payment_processing_service_app_v1
)
