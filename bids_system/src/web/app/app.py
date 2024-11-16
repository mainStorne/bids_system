import asyncio
import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .api.api import api
from contextlib import asynccontextmanager
from .conf import engine, BASE_PATH, templates
from .storage.db.setup import create_db_and_tables
from fastapi_pagination import add_pagination


@asynccontextmanager
async def lifespan(app):
    await create_db_and_tables(engine)
    yield

logging.basicConfig(level=logging.INFO)
app = FastAPI(root_path='/api', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=BASE_PATH / 'static'), name='static')
@app.get('/')
async def hello(request: Request):
    return templates.TemplateResponse(request, name='index.html')

app.include_router(api)
add_pagination(app)