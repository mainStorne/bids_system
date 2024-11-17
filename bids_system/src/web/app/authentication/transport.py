from fastapi.security import OAuth2PasswordBearer
from fastapi_users.authentication.transport.bearer import BearerTransport as _BearerTransport


class BearerTransport(_BearerTransport):
    def __init__(self, tokenUrl: str, scopes: dict[str, str]):
        self.scheme = OAuth2PasswordBearer(tokenUrl, auto_error=False)
