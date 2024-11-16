from inspect import Signature, Parameter
from typing import Optional, Sequence, cast, Callable
from fastapi import status, Depends, HTTPException
from fastapi_users.authentication import AuthenticationBackend, Strategy
from fastapi_users.authentication.authenticator import Authenticator as _Authenticator, DuplicateBackendNamesError, \
    EnabledBackendsDependency, name_to_variable_name, name_to_strategy_variable_name
from ..storage.db.models import User

class Authenticator(_Authenticator):

    def __init__(
            self,
            backends: Sequence[AuthenticationBackend],
            get_session
    ):
        self.get_session = get_session
        self.backends = backends

    async def _authenticate(
        self,
        *args,
        session,
        optional: bool = False,
        active: bool = False,
        verified: bool = False,
        superuser: bool = False,
        **kwargs,
    ) -> tuple[Optional[User], Optional[str]]:
        user: User | None = None
        token: Optional[str] = None
        enabled_backends: Sequence[AuthenticationBackend] = (
            kwargs.get("enabled_backends", self.backends)
        )
        for backend in self.backends:
            if backend in enabled_backends:
                token = kwargs[name_to_variable_name(backend.name)]
                strategy: Strategy = kwargs[
                    name_to_strategy_variable_name(backend.name)
                ]
                if token is not None:
                    user = await strategy.read_token(token, session)
                    if user:
                        break

        status_code = status.HTTP_401_UNAUTHORIZED
        if user:
            status_code = status.HTTP_403_FORBIDDEN
            if active and not user.is_active:
                status_code = status.HTTP_401_UNAUTHORIZED
                user = None
            elif (
                verified and not user.is_verified or superuser and not user.is_superuser
            ):
                user = None
        if not user and not optional:
            raise HTTPException(status_code=status_code)
        return user, token

    def _get_dependency_signature(
        self, get_enabled_backends: Optional[EnabledBackendsDependency] = None
    ) -> Signature:
        """
        Generate a dynamic signature for the current_user dependency.

        Here comes some blood magic 🧙‍♂️
        Thank to "makefun", we are able to generate callable
        with a dynamic number of dependencies at runtime.
        This way, each security schemes are detected by the OpenAPI generator.
        """
        try:
            parameters: list[Parameter] = [
                Parameter(
                    name="session",
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(self.get_session),
                )
            ]

            for backend in self.backends:
                parameters += [
                    Parameter(
                        name=name_to_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(cast(Callable, backend.transport.scheme)),
                    ),
                    Parameter(
                        name=name_to_strategy_variable_name(backend.name),
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(backend.get_strategy),
                    ),
                ]

            if get_enabled_backends is not None:
                parameters += [
                    Parameter(
                        name="enabled_backends",
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=Depends(get_enabled_backends),
                    )
                ]
            return Signature(parameters)
        except ValueError:
            raise DuplicateBackendNamesError()