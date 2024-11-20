from pydantic import BaseModel, ConfigDict
from fastapi_sqlalchemy_toolkit import make_partial_model



class RoleBase(BaseModel):
    name: str




class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int


class MyRoles(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    roles: list[RoleRead]




RoleUpdate = make_partial_model(RoleCreate)
