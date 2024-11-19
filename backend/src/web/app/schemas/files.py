from pydantic import BaseModel
from fastapi_sqlalchemy_toolkit import make_partial_model


# TODO: также обсудить что делать если нужно будет отправлять файл или ссылку, как в прошлый раз?
class BaseFile(BaseModel):
    name: str
    file_path: str


class FileRead(BaseFile):
    id: int


class FileCreate(BaseFile):
    pass


FileUpdate = make_partial_model(FileCreate)