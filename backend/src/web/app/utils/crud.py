from crud import CRUDTemplate
from ..dependencies.user import get_current_user, Permission, get_user_principals
from crud.openapi_responses import (
    missing_token_or_inactive_user_response, auth_responses, not_found_response,
)
from fastapi_permissions import has_permission
from typing import Any, TypeVar
from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

Resource = TypeVar('Resource')

class CrudAPIRouter(CRUDTemplate):

    def _get_all(self, *args: Any, **kwargs: Any):



        async def func(request: Request, session: AsyncSession = Depends(self.get_session), ):
            return await self.manager.list(session)

        @self.get(
            path='/',
            response_model=list[self.schema],
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response}

        )
        async def filter_operation(
                resources: list[Resource] = Depends(func),
                principals: list = Depends(get_user_principals),
                # acls: list = Permission("batch", AclBatchPermission)
        ):
            allowed = [item for item in resources if has_permission(principals, "view", item)]

    def _get_one(self, *args: Any, **kwargs: Any):
        async def func(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.get_or_404(session, id=id)

        @self.get(
            path='/{id}',
            response_model=self.schema,
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response, **not_found_response}

        )
        async def route(resource=Permission('view', func)):
            return resource

    def _create(self, *args: Any, **kwargs: Any):
        create_schema = self.create_schema

        async def func(request: Request, objs: create_schema, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.create(session, objs)

        @self.post(
            '/',
            response_model=self.schema,
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response}
        )
        async def route(resource=Permission('create', func)):
            return resource

    def _update(self, *args: Any, **kwargs: Any):
        update_schema = self.update_schema


        async def func(request: Request, id: int, scheme: update_schema,
                        session: AsyncSession = Depends(self.get_session)):
            model = await self.manager.get_or_404(session, id=id)
            return await self.manager.update(session, model, scheme)

        @self.patch(
            '/{id}',
            response_model=self.schema,
            dependencies=[Depends(get_current_user(superuser=True))],
            responses={**missing_token_or_inactive_user_response,
                       }
        )
        async def route(resource=Permission('edit', func)):
            return resource

    def _delete_all(self, *args: Any, **kwargs: Any):


        async def func(request: Request, session: AsyncSession = Depends(self.get_session)):
            for model in await self.manager.list(session):
                await session.delete(model)
            await session.commit()
            return

        @self.delete(
            '/',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_current_user(superuser=True))],
            responses={**auth_responses}
        )
        async def route(resource=Permission('delete_all', func)):
            return resource



    def _delete_one(self, *args: Any, **kwargs: Any):

        async def func(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            obj_in_db = await self.manager.get_or_404(session, id=id)
            await self.manager.delete(session, obj_in_db)
            return

        @self.delete(
            '/{id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_current_user(superuser=True))],
            responses={**auth_responses, **not_found_response}
        )
        async def route(resource=Permission('delete', func)):
            return resource

