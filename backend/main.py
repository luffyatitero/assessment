from contextlib import asynccontextmanager
from fastapi import FastAPI

from db import create_db_and_tables

from routes import router as main_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(main_router)