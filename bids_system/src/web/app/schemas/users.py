from datetime import datetime
from fastapi_sqlalchemy_toolkit import make_partial_model

from pydantic import BaseModel, Field


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


class CreateUser(BaseUser):
    password: str


class ReadUser(BaseUser):
    id: int



UpdateUser = make_partial_model(CreateUser)
