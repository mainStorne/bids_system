from typing import Callable, Any, List

from fastapi_sqlalchemy_toolkit.model_manager import ModelT
from sqlalchemy import UnaryExpression, Row, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from storage.db.models import UserRole, Role
from .base import BaseManager
from logging import getLogger



class RoleManager(BaseManager):

    def __init__(self,
                 default_ordering: InstrumentedAttribute | UnaryExpression | None = None,
                 ) -> None:
        super().__init__(Role, default_ordering)

    async def get_my_roles(
            self,
            session: AsyncSession,
            user_id: int,
            order_by: InstrumentedAttribute | UnaryExpression | None = None,
            filter_expressions: dict[InstrumentedAttribute | Callable, Any] | None = None,
            nullable_filter_expressions: (
                    dict[InstrumentedAttribute | Callable, Any] | None
            ) = None,
            options: List[Any] | Any | None = None,
            where: Any | None = None,
            *,
            unique: bool = False,
            **simple_filters: Any,
    ) -> List[ModelT] | List[Row]:
        stmt = select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
        res = await super().list(session, order_by, filter_expressions, nullable_filter_expressions, options, where,
                                  stmt,
                                  unique=unique, **simple_filters)

        result = []
        for r in res:
            result.append(r[0])
        return result

