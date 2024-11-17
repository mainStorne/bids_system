import asyncio
import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .api.api import api
from contextlib import asynccontextmanager
from .conf import engine
from .storage.db.setup import create_db_and_tables
from fastapi_pagination import add_pagination


@asynccontextmanager
async def lifespan(app):
    await create_db_and_tables(engine)
    yield

logging.basicConfig(level=logging.INFO)
app = FastAPI(root_path='/api', lifespan=lifespan)

app.include_router(api)
add_pagination(app)