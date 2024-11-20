from typing import Optional
import jwt
from fastapi_users import models
from fastapi_users.jwt import decode_jwt, generate_jwt
from fastapi_users.authentication.strategy import JWTStrategy as _JWTStrategy
from sqlalchemy.ext.asyncio import AsyncSession
from storage.db.models import User
class JWTStrategy(_JWTStrategy):

    async def read_token(
        self, token: Optional[str], session: AsyncSession,
    ) -> Optional[models.UP]:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            user_id = int(data.get("sub"))
            if user_id is None:
                return None
        except (jwt.PyJWTError, ValueError):
            return None
        return await session.get(User, user_id)


    async def write_token(self, user: User) -> str:
        # token_urlsafe()
        data = {"sub": str(user.id), "aud": self.token_audience}
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )



