from fastapi.security import OAuth2PasswordBearer
from fastapi_users.authentication.transport.bearer import BearerTransport as _BearerTransport
from fastapi_users.openapi import OpenAPIResponseType
from starlette import status
from starlette.responses import Response
from crud.openapi_responses import no_content_response


class BearerTransport(_BearerTransport):
    def __init__(self, tokenUrl: str, scopes: dict[str, str]):
        self.scheme = OAuth2PasswordBearer(tokenUrl, auto_error=False)


    async def get_logout_response(self) -> Response:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


    def get_openapi_logout_responses_success(self) -> OpenAPIResponseType:
        return no_content_response
