from typing import Any

from fastapi_permissions import Allow
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, UploadFile, HTTPException, status

from ...exceptions import FileDoesntSave
from ...schemas.users import ReadUser, CreateUser, UpdateUser
from ...schemas.files import FileRead
from ...utils.users import user_manager
from ...utils.crud import CrudAPIRouter
from ...managers import BaseManager, FilesManager
from ...dependencies.user import get_current_user, user_or_404, Permission
from ...dependencies.session import get_session
from storage.db.models import Role, File, User
from crud.openapi_responses import missing_token_or_inactive_user_response, not_found_response, conflict_response
from logging import getLogger
from crud import Context

logger = getLogger(__name__)

role_manager = BaseManager(Role)
files_manager = FilesManager(File)

r = APIRouter()


class Crud(CrudAPIRouter):
    def _create(self, *args: Any, **kwargs: Any):
        create_schema = self.create_schema

        @self.post(
            '/register',
            response_model=self.schema,
        )
        async def route(request: Request, objs: create_schema, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.create(session, objs)

    def _get_one(self, *args: Any, **kwargs: Any):

        def get_acls(user: User):
            return [
            (Allow, f'user:{user.login}', 'view'),
        ]

        async def func(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            user1 = await session.get(User, id)
            user: User = await self.manager.get_or_404(session, id=id)
            logger.info('response from crud %s', user)
            principals = get_acls(user)
            # logger.info('user dict is %s', user.__acl__())
            logger.info('user1 dict is %s', user1.__acl__())
            logger.info('acls %s', principals)
            return user

        @self.get(
            path='/{id}',
            response_model=self.schema,
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response, **not_found_response}

        )
        async def route(user: User = Permission('view', func)):
            return user


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
       dependencies=[Depends(get_current_user(active=True)), Depends(user_or_404)]
       )
async def files(session: AsyncSession = Depends(get_session)):
    return await files_manager.list(session, user=[id])


@r.post('/{id}/files',
        response_model=FileRead,
        responses={**missing_token_or_inactive_user_response, **not_found_response,
                   **conflict_response,
                   }
        )
async def files(upload_file: UploadFile, user=Depends(user_or_404), session: AsyncSession = Depends(get_session)):
    # TODO: maybe create multiple upload files?
    try:
        return await files_manager.create_user_file(session, upload_file, user=[user.id])
    except FileDoesntSave:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)


r.include_router(crud)
