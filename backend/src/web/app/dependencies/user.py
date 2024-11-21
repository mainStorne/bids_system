from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_permissions import Everyone, Authenticated, Allow, configure_permissions
# from ..utils.permissions import configure_permissions
from ..utils.users import authenticator
from .session import get_session
from logging import getLogger
from ..utils.users import authenticator, user_manager

logger = getLogger(__name__)
get_current_user = authenticator.current_user


async def user_or_404(id: int, session: AsyncSession = Depends(get_session)):
    return await user_manager.get_or_404(session, id=id)


async def get_user_principals(user=Depends(authenticator.current_user(active=True))):
    principals = await user.principals()
    principals = principals + [Authenticated, Everyone]
    logger.info('user principals %s', principals)
    return principals


AclBatchPermission = [(Allow, 'role:admin', 'view')]

Permission = configure_permissions(get_user_principals)
