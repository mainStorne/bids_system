from .settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from pathlib import Path
from redis.asyncio import ConnectionPool

BASE_PATH = Path(__file__).absolute().parent
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
connection_pool = ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)