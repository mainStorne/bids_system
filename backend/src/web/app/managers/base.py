from fastapi_sqlalchemy_toolkit import ModelManager
from logging import getLogger


logger = getLogger("managers")


class BaseManager(ModelManager):
    pass