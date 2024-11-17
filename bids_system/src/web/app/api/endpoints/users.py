from typing import Any, Annotated

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import joinedload, InstrumentedAttribute

from ...schemas.users import ReadUser, CreateUser, UpdateUser
from ...utils.users import user_manager
from web.crud import RouteDict
from ...utils.crud import CrudAPIRouter
from ...managers import BaseManager
from ...dependencies.user import get_user
from ...dependencies.session import get_session
from ...storage.db.models import User, Role, UserRole
from web.crud.openapi_responses import missing_token_or_inactive_user_response
from logging import getLogger

logger = getLogger(__name__)


role_manager = BaseManager(Role)


class Crud(CrudAPIRouter):
    def _create(self, *args: Any, **kwargs: Any):
        async def route(request: Request, objs: CreateUser, session: AsyncSession = Depends(self.get_session)):
            async with session.begin():
                stmt = select(Role).where(Role.name == 'role:costumer')
                costumer_role = await session.scalar(stmt)

                user: User = await self.manager.create(session, objs, roles=[costumer_role.id])
                user_role = Role(name=f'user:{user.id}')
                user_role.users = [user]
                session.add(user_role)

            await session.refresh(user, ['roles'])
            logger.info(user.roles)
            return user

        return route


r = APIRouter()
crud = Crud(user_manager,
            ReadUser, CreateUser, UpdateUser,
            create_route=RouteDict(name='register:register', path='/register', )
            )


@r.get('/me',
       response_model=ReadUser,
       responses={**missing_token_or_inactive_user_response})
async def me(user=Depends(get_user(active=True))):
    return user


@r.patch('/me',
         response_model=ReadUser,
         responses={**missing_token_or_inactive_user_response},
         )
async def me(update_to: UpdateUser,
             user=Depends(get_user(active=True)),
             session=Depends(get_session)):
    return await user_manager.update(session, user, update_to)





r.include_router(crud)
