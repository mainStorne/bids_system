from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, Request, status
from ...schemas.users import ReadUser, CreateUser, UpdateUser
from ...utils.users import user_manager
from web.crud import RouteDict
from ...utils.crud import CrudAPIRouter
from ...managers import BaseManager
from ...storage.db.models import UserType
from ...dependencies.user import get_current_user
from ...dependencies.session import get_session
from web.crud.openapi_responses import missing_token_or_inactive_user_response

user_type_manager = BaseManager(UserType)


class Crud(CrudAPIRouter):
    def _create(self, *args: Any, **kwargs: Any):
        async def route(request: Request, objs: CreateUser, session: AsyncSession = Depends(self.get_session)):
            user_type = await user_type_manager.get(session, name='customer')
            return await self.manager.create(session, objs, type_id=user_type.id)

        return route


r = APIRouter()
crud = Crud(user_manager,
            ReadUser, CreateUser, UpdateUser,
            create_route=RouteDict(name='register:register', path='/register', )
            )


@r.get('/me',
       response_model=ReadUser,
       responses={**missing_token_or_inactive_user_response})
async def me(user=Depends(get_current_user(active=True))):
    return user


@r.patch('/me',
         response_model=ReadUser,
         responses={**missing_token_or_inactive_user_response},
         )
async def me(update_to: UpdateUser,
             user = Depends(get_current_user(active=True)),
             session=Depends(get_session)):
    return await user_manager.update(session, user, update_to)


r.include_router(crud)
