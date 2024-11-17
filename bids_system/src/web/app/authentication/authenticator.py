from inspect import Signature, Parameter
from typing import Optional, Sequence, cast, Callable, Any
from fastapi import status, Depends, HTTPException
from fastapi_users.authentication import AuthenticationBackend, Strategy
from fastapi_users.authentication.authenticator import Authenticator as _Authenticator, DuplicateBackendNamesError, \
    EnabledBackendsDependency, name_to_variable_name, name_to_strategy_variable_name
from makefun import with_signature
from logging import getLogger
from ..storage.db.models import User

logger = getLogger(__name__)

class Authenticator(_Authenticator):

    def __init__(
            self,
            backends: Sequence[AuthenticationBackend],
            get_session
    ):
        self.get_session = get_session
        self.backends = backends

    def current_user_token(
            self,
            optional: bool = False,
            active: bool = False,
            verified: bool = False,
            superuser: bool = False,
            get_enabled_backends: Optional[
                EnabledBackendsDependency
            ] = None,
            raise_on_absense: bool = False,
    ):
        """
        Return a dependency callable to retrieve currently authenticated user and token.

        :param optional: If `True`, `None` is returned if there is no authenticated user
        or if it doesn't pass the other requirements.
        Otherwise, throw `401 Unauthorized`. Defaults to `False`.
        Otherwise, an exception is raised. Defaults to `False`.
        :param active: If `True`, throw `401 Unauthorized` if
        the authenticated user is inactive. Defaults to `False`.
        :param verified: If `True`, throw `401 Unauthorized` if
        the authenticated user is not verified. Defaults to `False`.
        :param superuser: If `True`, throw `403 Forbidden` if
        the authenticated user is not a superuser. Defaults to `False`.
        :param get_enabled_backends: Optional dependency callable returning
        a list of enabled authentication backends.
        Useful if you want to dynamically enable some authentication backends
        based on external logic, like a configuration in database.
        By default, all specified authentication backends are enabled.
        Please not however that every backends will appear in the OpenAPI documentation,
        as FastAPI resolves it statically.
        """
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_token_dependency(*args: Any, **kwargs: Any):
            return await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                raise_on_absense=raise_on_absense,
                **kwargs,
            )

        return current_user_token_dependency

    def current_user(
            self,
            optional: bool = False,
            active: bool = False,
            verified: bool = False,
            superuser: bool = False,
            get_enabled_backends: Optional[
                EnabledBackendsDependency
            ] = None,
            raise_on_absense: bool = False,
    ):
        """
        Return a dependency callable to retrieve currently authenticated user.

        :param optional: If `True`, `None` is returned if there is no authenticated user
        or if it doesn't pass the other requirements.
        Otherwise, throw `401 Unauthorized`. Defaults to `False`.
        Otherwise, an exception is raised. Defaults to `False`.
        :param active: If `True`, throw `401 Unauthorized` if
        the authenticated user is inactive. Defaults to `False`.
        :param verified: If `True`, throw `401 Unauthorized` if
        the authenticated user is not verified. Defaults to `False`.
        :param superuser: If `True`, throw `403 Forbidden` if
        the authenticated user is not a superuser. Defaults to `False`.
        :param get_enabled_backends: Optional dependency callable returning
        a list of enabled authentication backends.
        Useful if you want to dynamically enable some authentication backends
        based on external logic, like a configuration in database.
        By default, all specified authentication backends are enabled.
        Please not however that every backends will appear in the OpenAPI documentation,
        as FastAPI resolves it statically.
        """
        signature = self._get_dependency_signature(get_enabled_backends)

        @with_signature(signature)
        async def current_user_dependency(*args: Any, **kwargs: Any):
            user, _ = await self._authenticate(
                *args,
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                raise_on_absense=raise_on_absense,
                **kwargs,
            )
            return user

        return current_user_dependency

    async def _authenticate(self, *args,
                            optional: bool = False,
                            active: bool = False,
                            verified: bool = False,
                            superuser: bool = False,
                            get_enabled_backends: Optional[
                                EnabledBackendsDependency] = None,
                            raise_on_absense: bool, session, **kwargs) -> tuple[Optional[User], Optional[str]]:
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
                    logger.info(user)
                    if user:
                        return user, token

        if raise_on_absense:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        #
        # if user:
        #     status_code = status.HTTP_403_FORBIDDEN
        #     if active and not user.is_active:
        #         status_code = status.HTTP_401_UNAUTHORIZED
        #         user = None
        #     elif (
        #         verified and not user.is_verified or superuser and not user.is_superuser
        #     ):
        #         user = None
        # if not user and not optional:
        #     raise HTTPException(status_code=status_code)

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
