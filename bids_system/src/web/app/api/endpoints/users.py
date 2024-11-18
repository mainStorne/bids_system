from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request
from ...schemas.users import ReadUser, CreateUser, UpdateUser
from ...schemas.files import FileRead
from ...utils.users import user_manager
from ...utils.crud import CrudAPIRouter
from ...managers import BaseManager
from ...dependencies.user import get_current_user
from ...dependencies.session import get_session
from ...storage.db.models import Role, File
from crud.openapi_responses import missing_token_or_inactive_user_response, not_found_response
from logging import getLogger
from crud import Context

logger = getLogger(__name__)

role_manager = BaseManager(Role)
file_manager = BaseManager(File)

r = APIRouter()


class Crud(CrudAPIRouter):
    def _create(self, *args: Any, **kwargs: Any):
        create_schema = self.create_schema

        @self.post(
            '/register',
            response_model=self.schema,
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response,
                       }
        )
        async def route(request: Request, objs: create_schema, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.create(session, objs)


ctx = Context(manager=user_manager, get_session=get_session,
              schema=ReadUser, create_schema=CreateUser, update_schema=UpdateUser
              )
crud = Crud(ctx)


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
             user=Depends(get_current_user(active=True)),
             session=Depends(get_session)):
    return await user_manager.update(session, user, update_to)


@r.get('/{id}/files',
       response_model=list[FileRead],
       responses={**missing_token_or_inactive_user_response, **not_found_response},
       dependencies=[Depends(get_current_user(active=True))]
       )
async def files(id: int, session: AsyncSession = Depends(get_session)):
    await user_manager.get_or_404(session, id=id)
    return await file_manager.list(session, user=[id])


@r.post('/{id}/files',
        response_model=FileRead,
        responses={**missing_token_or_inactive_user_response, **not_found_response}
        )
async def files(id: int, session: AsyncSession = Depends(get_session)):
    user = await user_manager.get_or_404(session, id=id)
    return await file_manager.create(session, user=[user.id])


r.include_router(crud)
