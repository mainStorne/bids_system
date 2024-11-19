from fastapi import Depends
from fastapi_permissions import Everyone, Authenticated, configure_permissions
from ..utils.users import authenticator


async def get_user_principals(user=Depends(authenticator.current_user(active=True))):
    principals = await user.principals()
    return principals + [Authenticated, Everyone]


Permission = configure_permissions(get_user_principals)
