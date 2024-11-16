from typing import Type, Optional, Union, Any, List

from fastapi import Depends, Request
from fastapi_sqlalchemy_toolkit import ModelManager
from sqlalchemy.ext.asyncio import AsyncSession

from .crud_generator import CRUDGenerator, PydanticModelT, RouteDict


class CrudAPIRouter(CRUDGenerator[PydanticModelT]):
    def __init__(
            self,
            manager: ModelManager,
            get_session,
            schema: Type[PydanticModelT],
            create_schema: Optional[Type[PydanticModelT]] = None,
            update_schema: Optional[Type[PydanticModelT]] = None,
            prefix: Optional[str] = None,
            tags: Optional[List[str]] = None,
            paginate: Optional[int] = None,
            get_all_route: RouteDict = None,
            get_one_route: RouteDict = None,
            create_route: RouteDict = None,
            update_route: RouteDict = None,
            delete_one_route: RouteDict = None,
            delete_all_route: RouteDict = None,
            **kwargs: Any,
    ) -> None:
        self.manager = manager
        self.get_session = get_session

        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix or self.manager.model.__tablename__,
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            **kwargs
        )

    def _get_all(self, *args: Any, **kwargs: Any):
        async def route(request: Request, session: AsyncSession = Depends(self.get_session), ):
            return await self.manager.list(session)

        return route

    def _get_one(self, *args: Any, **kwargs: Any):
        async def route(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.get_or_404(session, id=id)

        return route

    def _create(self, *args: Any, **kwargs: Any):
        create_schema = self.create_schema

        async def route(request: Request, objs: create_schema, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.create(session, objs)

        return route

    def _update(self, *args: Any, **kwargs: Any):
        update_schema = self.update_schema

        async def route(request: Request, id: int, scheme: update_schema,
                        session: AsyncSession = Depends(self.get_session)):
            model = await self.manager.get_or_404(session, id=id)
            return await self.manager.update(session, model, scheme)

        return route

    def _delete_all(self, *args: Any, **kwargs: Any):
        async def route(request: Request, session: AsyncSession = Depends(self.get_session)):
            for model in await self.manager.list(session):
                await session.delete(model)
            await session.commit()
            return

        return route

    def _delete_one(self, *args: Any, **kwargs: Any):
        async def route(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            obj_in_db = await self.manager.get_or_404(session, id=id)
            await self.manager.delete(session, obj_in_db)
            return

        return route
