from typing import Optional

from fastapi.security.utils import get_authorization_scheme_param
from fastapi_users.authentication.transport.bearer import BearerTransport as _BearerTransport
from fastapi_users.openapi import OpenAPIResponseType
from fastapi import Response, Request, status, HTTPException

from crud.openapi_responses import no_content_response
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

class TokenBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "refresher":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "refresher"},
                )
            else:
                return None
        return param

class TokenResponse(BaseModel):
    token_type: str = 'refresher'
    access_token: str
    refresh_token: str


class BearerTransport(_BearerTransport):

    def __init__(self, tokenUrl: str, scopes: dict[str, str]):
        self.scheme = TokenBearer(tokenUrl, auto_error=False)


    async def get_login_response(self, token: dict):
        return {'token_type': 'refresher', **token}

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": TokenResponse,
            },
        }




    async def get_logout_response(self) -> Response:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


    def get_openapi_logout_responses_success(self) -> OpenAPIResponseType:
        return no_content_response
