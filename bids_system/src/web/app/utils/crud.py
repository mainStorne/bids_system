from web.crud import CRUDTemplate
from ..dependencies.user import get_current_user
from web.crud.openapi_responses import (
    missing_token_or_inactive_user_response, auth_responses, not_found_response,
)
from typing import Any
from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession


class CrudAPIRouter(CRUDTemplate):


    def _get_all(self, *args: Any, **kwargs: Any):
        @self.get(
            path='/',
            response_model=list[self.schema],
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response}

        )
        async def route(request: Request, session: AsyncSession = Depends(self.get_session), ):
            return await self.manager.list(session)

    def _get_one(self, *args: Any, **kwargs: Any):
        @self.get(
            path='/{id}',
            response_model=self.schema,
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response, **not_found_response}

        )
        async def route(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.get_or_404(session, id=id)


    def _create(self, *args: Any, **kwargs: Any):
        create_schema = self.create_schema

        @self.post(
            '/',
            response_model=self.schema,
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response,
                       }
        )
        async def route(request: Request, objs: create_schema, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.create(session, objs)


    def _update(self, *args: Any, **kwargs: Any):
        update_schema = self.update_schema
        @self.patch(
            '/{id}',
            response_model=self.schema,
            dependencies=[Depends(get_current_user(superuser=True))],
            responses={**missing_token_or_inactive_user_response,
                       }
        )
        async def route(request: Request, id: int, scheme: update_schema,
                        session: AsyncSession = Depends(self.get_session)):
            model = await self.manager.get_or_404(session, id=id)
            return await self.manager.update(session, model, scheme)


    def _delete_all(self, *args: Any, **kwargs: Any):
        @self.delete(
            '/',
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies = [Depends(get_current_user(superuser=True))],
        responses = {**auth_responses}
        )
        async def route(request: Request, session: AsyncSession = Depends(self.get_session)):
            for model in await self.manager.list(session):
                await session.delete(model)
            await session.commit()
            return


    def _delete_one(self, *args: Any, **kwargs: Any):
        @self.delete(
            '/{id}',
            status_code=status.HTTP_204_NO_CONTENT,
            dependencies=[Depends(get_current_user(superuser=True))],
            responses={**auth_responses, **not_found_response}
        )
        async def route(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            obj_in_db = await self.manager.get_or_404(session, id=id)
            await self.manager.delete(session, obj_in_db)
            return
