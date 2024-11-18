from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .session import get_session
from ..utils.users import authenticator, user_manager

get_current_user = authenticator.current_user


async def user_or_404(id: int, session: AsyncSession = Depends(get_session)):
    return await user_manager.get_or_404(session, id=id)