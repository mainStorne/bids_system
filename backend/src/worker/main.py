import asyncio
from saq import CronJob, Queue
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from logging import getLogger, basicConfig, INFO, DEBUG
from .settings import settings as conf_settings

logger = getLogger(__name__)


# all functions take in context dict and kwargs
async def test(ctx, *, a):
    await asyncio.sleep(0.5)
    # result should be json serializable
    # custom serializers and deserializers can be used through Queue(dump=,load=)
    return {"x": a}


async def cron(ctx):
    # raise Exception
    logger.info('ctx %s', ctx)


async def startup(ctx):
    logger.info('ctx %s', ctx)
    logger.info('settings %s', conf_settings)
    engine = create_async_engine(conf_settings.SQLALCHEMY_DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    ctx["async_session_maker"] = async_session_maker


async def shutdown(ctx):
    pass
    # await ctx["db"].disconnect()


async def before_process(ctx):
    pass
    # print(ctx["job"], ctx["db"])


async def after_process(ctx):
    pass


queue = Queue.from_url(f'redis://{conf_settings.REDIS_HOST}')

settings = {
    "queue": queue,
    "functions": [test],
    "concurrency": 10,
    "cron_jobs": [CronJob(cron, cron="* * * * * */5")],  # run every 5 seconds
    "startup": startup,
    "shutdown": shutdown,
    "before_process": before_process,
    "after_process": after_process,
}
