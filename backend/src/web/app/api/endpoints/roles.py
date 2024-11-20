from typing import Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from crud import Context
from crud.openapi_responses import missing_token_or_inactive_user_response, not_found_response
from ...dependencies.session import get_session
from ...dependencies.user import get_current_user, Permission
from ...utils.crud import CrudAPIRouter
from ...managers import RoleManager
from storage.db.models import Role
from ...schemas.roles import RoleCreate, RoleRead, RoleUpdate
from fastapi import APIRouter

role_manager = RoleManager()


class Crud(CrudAPIRouter):
    def _get_one(self, *args: Any, **kwargs: Any):

        async def func(request: Request, id: int, session: AsyncSession = Depends(self.get_session)):
            return await self.manager.get_or_404(session, id=id)

        @self.get(
            path='/{id}',
            response_model=self.schema,
            dependencies=[Depends(get_current_user())],
            responses={**missing_token_or_inactive_user_response, **not_found_response}

        )
        async def route(role: Role = Permission('view', func)):
            return role





ctx = Context(manager=role_manager, get_session=get_session,
        schema=RoleRead, create_schema=RoleCreate, update_schema=RoleUpdate
        )

crud = Crud(ctx)


r = APIRouter()

@r.get('/my', response_model=list[RoleRead], responses={
    **missing_token_or_inactive_user_response
})
async def my_roles(user = Depends(get_current_user(active=True)),
                   session = Depends(get_session)):
    return await role_manager.get_my_roles(session, user.id)


r.include_router(crud)