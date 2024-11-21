from typing import Iterable, Any, Optional

from fastapi.security import OAuth2PasswordRequestForm
from fastapi_sqlalchemy_toolkit.model_manager import CreateSchemaT, ModelT
from fastapi_users.password import PasswordHelperProtocol, PasswordHelper
from sqlalchemy import UnaryExpression, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from storage.db.models import User, Role
from .base import BaseManager


class UsersManager(BaseManager):

    def __init__(self,
                 default_ordering: InstrumentedAttribute | UnaryExpression | None = None,
                 password_helper: Optional[PasswordHelperProtocol] = None,
                 ) -> None:
        if password_helper is None:
            self.password_helper = PasswordHelper()
        else:
            self.password_helper = password_helper  # pragma: no cover
        super().__init__(User, default_ordering)

    async def create(
            self,
            session: AsyncSession,
            in_obj: CreateSchemaT | None = None,
            refresh_attribute_names: Iterable[str] | None = None,
            *,
            commit: bool = True,
            **attrs: Any,
    ) -> ModelT:
        async with session.begin():
            in_obj.password = self.password_helper.hash(in_obj.password)
            user = await super().create(session, in_obj, ['roles'], commit=False, **attrs)
            stmt = select(Role).where(Role.name == 'role:costumer')
            costumer_role = await session.scalar(stmt)
            user.roles = [costumer_role]

        return user

    async def authenticate(self, session: AsyncSession, credentials: OAuth2PasswordRequestForm):
        stmt = select(self.model).where(self.model.login == credentials.username)
        user = (await session.execute(stmt)).scalar()
        if not user:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            user.password = updated_password_hash
            session.add(user)
            await session.commit()

        return user
