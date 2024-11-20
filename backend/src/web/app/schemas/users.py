from datetime import datetime
from fastapi_sqlalchemy_toolkit import make_partial_model
from fastapi_permissions import Authenticated, Deny, Allow, All
from pydantic import BaseModel, Field, ConfigDict


class BaseUser(BaseModel):
    login: str
    phone: str
    first_name: str
    middle_name: str
    last_name: str

    # TODO: change this on read user
    is_superuser: bool
    is_active: bool
    is_verified: bool

    def __acl__(self):
        return [
            (Allow, f'user:{self.login}', 'view'),
            # (Allow, 'role:admin', All),
            # (Allow, f'user:{self.login}', All)
        ]



class CreateUser(BaseUser):
    password: str



class ReadUser(BaseUser):
    id: int


UpdateUser = make_partial_model(CreateUser)

