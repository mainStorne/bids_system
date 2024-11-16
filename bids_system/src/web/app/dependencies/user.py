from typing import Optional

from fastapi import Depends
from fastapi_users.authentication.authenticator import EnabledBackendsDependency
from ..utils.users import authenticator
from ..storage.db.models import User


def get_current_user(optional: bool = False,
                     active: bool = False,
                     verified: bool = False,
                     superuser: bool = False,
                     get_enabled_backends: Optional[EnabledBackendsDependency] = None):
    dependency = authenticator.current_user(
        optional, active, verified, superuser, get_enabled_backends
    )

    async def get_current_user(user: User = Depends(dependency)):
        return user

    return get_current_user
