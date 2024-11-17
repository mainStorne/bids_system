from typing import Optional, List, Type

from fastapi import Depends

from web.crud import CrudAPIRouter as _CrudAPIRouter, RouteDict
from web.crud.crud_generator import PydanticModelT
from fastapi_sqlalchemy_toolkit import ModelManager
from ..dependencies.user import get_user
from ..dependencies.session import get_session
from web.crud.openapi_responses import (
    missing_token_or_inactive_user_response, auth_responses, not_found_response,
)


class CrudAPIRouter(_CrudAPIRouter):
    def __init__(
            self,
            manager: ModelManager,
            schema: type[PydanticModelT],
            create_schema: Optional[Type[PydanticModelT]] = None,
            update_schema: Optional[Type[PydanticModelT]] = None,
            prefix: Optional[str] = None,
            tags: Optional[List[str]] = None,
            get_all_route: RouteDict = None,
            get_one_route: RouteDict = None,
            create_route: RouteDict = None,
            update_route: RouteDict = None,
            delete_one_route: RouteDict = None,
            delete_all_route: RouteDict = None,
            **kwargs
    ) -> None:
        get_all_route = get_all_route or RouteDict(dependencies=[Depends(get_user())],
                                                   responses={**missing_token_or_inactive_user_response})
        get_one_route = get_one_route or RouteDict(dependencies=[Depends(get_user())],
                                                   responses={**missing_token_or_inactive_user_response,
                                                              **not_found_response})
        create_route = create_route or RouteDict(dependencies=[Depends(get_user())],
                                                 responses={**missing_token_or_inactive_user_response,
                                                            })
        update_route = update_route or RouteDict(dependencies=[Depends(get_user(superuser=True))],
                                                 responses={**missing_token_or_inactive_user_response,
                                                            })
        delete_all_route = delete_all_route or RouteDict(dependencies=[Depends(get_user(superuser=True))],
                                                         responses={**auth_responses})
        delete_one_route = delete_one_route or RouteDict(dependencies=[Depends(get_user(superuser=True))],
                                                         responses={**auth_responses,
                                                                    **not_found_response})
        super().__init__(
            schema=schema,
            manager=manager,
            get_session=get_session,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix or manager.model.__tablename__,
            tags=tags,
            paginate=False,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_all_route=delete_all_route,
            delete_one_route=delete_one_route,
            **kwargs
        )
