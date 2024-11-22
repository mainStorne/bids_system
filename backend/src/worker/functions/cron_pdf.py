from aiohttp import ClientSession
from bs4 import BeautifulSoup

async def fetch_pdf(url: str = 'https://www.minsport.gov.ru/activity/government-regulation/edinyj-kalendarnyj-plan/'):
    async with ClientSession() as session:
        await session.get(url, ssl=False)