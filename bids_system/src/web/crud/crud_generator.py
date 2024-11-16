from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Optional, Type, Union, TypeVar, TypedDict

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from .openapi_responses import not_found_response

PydanticModelT = TypeVar("PydanticModelT", bound=BaseModel)
NOT_FOUND = HTTPException(404, "Item not found")


class RouteDict(TypedDict, total=False):
    path: str
    name: str
    dependencies: list[Depends]
    responses: dict


class CRUDGenerator(Generic[PydanticModelT], APIRouter, ABC):
    schema: Type[PydanticModelT]
    create_schema: Type[PydanticModelT]
    update_schema: Type[PydanticModelT]
    _base_path: str = "/"

    def __init__(
            self,
            schema: Type[PydanticModelT],
            create_schema: Optional[Type[PydanticModelT]] = None,
            update_schema: Optional[Type[PydanticModelT]] = None,
            prefix: Optional[str] = None,
            tags: Optional[List[str]] = None,
            paginate: Optional[int] = None,
            get_all_route: RouteDict = None,
            get_one_route: RouteDict = None,
            create_route: RouteDict = None,
            update_route: RouteDict = None,
            delete_one_route: RouteDict = None,
            delete_all_route: RouteDict = None,
            **kwargs: Any,
    ) -> None:


        self.schema = schema
        self.create_schema = create_schema
        self.update_schema = update_schema

        super().__init__(**kwargs)

        if get_all_route:
            self.add_api_route(
                **{'path': "/",
                   'endpoint': self._get_all(),
                   'methods': ["GET"],
                   'response_model': List[self.schema],
                   'summary': "Get All",
                   **get_all_route
                   })

        if create_route:
            self.add_api_route(
                **{'path': "/",
                   'endpoint': self._create(),
                   'methods': ["POST"],
                   'response_model': self.schema,
                   'summary': "Create One",
                   'status_code': status.HTTP_201_CREATED,
                   **create_route
                   })


        if get_one_route:
            self.add_api_route(
                **{'path': "/{id}",
                   'endpoint': self._get_one(),
                   'methods': ["GET"],
                   'response_model': self.schema,
                   'summary': "Get One",
                   **get_one_route
                   })

        if update_route:
            self.add_api_route(
                **{'path': "/{id}",
                   'endpoint': self._update(),
                   'methods': ["PATCH"],
                   'response_model': self.schema,
                   'summary': "Update One",
                   **update_route
                   })

        if delete_one_route:
            self.add_api_route(
                **{'path': "/{id}",
                   'endpoint': self._delete_one(),
                   'methods': ["DELETE"],
                   'summary': "Delete One",
                   'status_code': status.HTTP_204_NO_CONTENT,
                   **delete_one_route
                   })


        if delete_all_route:
            self.add_api_route(
                **{'path': "/",
                   'endpoint': self._delete_all(),
                   'methods': ["DELETE"],
                   'summary': "Delete All",
                   'status_code': status.HTTP_204_NO_CONTENT,
                   **delete_all_route
                   })

    def api_route(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    # def get(
    #         self, path: str, *args: Any, **kwargs: Any
    # ) -> Callable[[DecoratedCallable], DecoratedCallable]:
    #     self.remove_api_route(path, ["Get"])
    #     return super().get(path, *args, **kwargs)
    #
    # def post(
    #         self, path: str, *args: Any, **kwargs: Any
    # ) -> Callable[[DecoratedCallable], DecoratedCallable]:
    #     self.remove_api_route(path, ["POST"])
    #     return super().post(path, *args, **kwargs)
    #
    # def put(
    #         self, path: str, *args: Any, **kwargs: Any
    # ) -> Callable[[DecoratedCallable], DecoratedCallable]:
    #     self.remove_api_route(path, ["PUT"])
    #     return super().put(path, *args, **kwargs)
    #
    # def delete(
    #         self, path: str, *args: Any, **kwargs: Any
    # ) -> Callable[[DecoratedCallable], DecoratedCallable]:
    #     self.remove_api_route(path, ["DELETE"])
    #     return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if (
                    route.path == path
                    and route.methods == methods_
            ):
                self.routes.remove(route)

    @abstractmethod
    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @abstractmethod
    def _delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

