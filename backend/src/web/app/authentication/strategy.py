from datetime import datetime, date, timezone
import time
from logging import getLogger
from typing import Optional
import jwt
from asyncpg.pgproto.pgproto import timedelta
from fastapi_users import models
from fastapi_users.jwt import decode_jwt, generate_jwt, SecretType
from fastapi_users.authentication.strategy import JWTStrategy as _JWTStrategy
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies.session import get_session
from ..dependencies.redis import get_redis
from contextlib import asynccontextmanager
from storage.db.models import User, Session

logger = getLogger(__name__)


class JWTStrategy(_JWTStrategy):

    def __init__(
            self,
            secret: SecretType,
            refresh_token_lifetime: timedelta,
            lifetime_seconds: timedelta,
            token_audience: list[str] = ["fastapi-users:auth"],
            algorithm: str = "HS256",
            public_key: Optional[SecretType] = None,
    ):
        super().__init__(secret, None, token_audience, algorithm, public_key)
        self.lifetime_seconds = lifetime_seconds
        self.refresh_token_lifetime = refresh_token_lifetime

    async def refresh_token(self, refresh_token: str):
        payload = self._decode_token(refresh_token)
        if payload is None:
            return payload

        async with asynccontextmanager(get_redis)() as redis:
            redis: Redis
            refresh_token = await redis.get(f'session:{payload["sid"]}')

        if refresh_token is None:
            return refresh_token

        access_token, refresh_token = self.generate_pair_of_tokens(payload)
        async with asynccontextmanager(get_redis)() as redis:
            redis: Redis
            await redis.set(f'session:{payload["sid"]}', refresh_token)

        return {'access_token': access_token, 'refresh_token': refresh_token, 'type': 'refresher'}

    def generate_pair_of_tokens(self, payload: dict):

        payload['exp'] = datetime.now(timezone.utc) + self.lifetime_seconds
        access_token = jwt.encode(payload.copy(), self.encode_key, algorithm=self.algorithm)
        payload['exp'] = datetime.now(timezone.utc) + self.refresh_token_lifetime
        refresh_token = jwt.encode(payload.copy(), self.encode_key, algorithm=self.algorithm)
        return access_token, refresh_token

    async def read_token(
            self, access_token: Optional[str], session: AsyncSession,
    ) -> Optional[models.UP]:
        if access_token is None:
            return None

        res = self._decode_token(access_token)

        if res is None:
            return res
        return await session.get(User, res['sub'])

    def _decode_token(self, token: str):
        try:
            payload = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            payload['sub'] = int(payload.get("sub"))
            payload['sid'] = int(payload.get('sid'))

        except (jwt.PyJWTError, ValueError, jwt.ExpiredSignatureError):
            return None
        return payload

    async def destroy_token(self, access_token: str, user: models.UP) -> None:
        res = self._decode_token(access_token)
        logger.info('res is %s', res)
        if res is None:
            return res

        async with asynccontextmanager(get_session)() as session:
            session: AsyncSession
            user_session = await session.get(Session, res['sid'])
            await session.delete(user_session)
            await session.commit()

        async with asynccontextmanager(get_redis)() as redis:
            redis: Redis
            await redis.delete(f'session:{user_session.id}')

    async def write_token(self, user: User) -> dict:
        async with asynccontextmanager(get_session)() as session:
            session: AsyncSession
            user_session = Session(user_id=user.id)
            session.add(user_session)
            await session.commit()

        payload = {"sub": str(user.id), "aud": self.token_audience, 'sid': str(user_session.id)}
        access_token, refresh_token = self.generate_pair_of_tokens(payload)

        logger.info('start execute redis ')
        async with asynccontextmanager(get_redis)() as redis:
            redis: Redis
            await redis.set(f'session:{user_session.id}', refresh_token)

        return {'access_token': access_token, 'refresh_token': refresh_token}
