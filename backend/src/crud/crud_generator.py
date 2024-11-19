from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, Optional, Type, Union, TypeVar, TypedDict

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.types import DecoratedCallable
from fastapi_sqlalchemy_toolkit import ModelManager
from pydantic import BaseModel
from .openapi_responses import not_found_response

NOT_FOUND = HTTPException(404, "Item not found")


class RouteDict(TypedDict, total=False):
    path: str
    name: str
    dependencies: list[Depends]
    responses: dict


class Context(TypedDict, total=False):
    schema: Type[BaseModel]
    manager: ModelManager
    get_session: Callable
    create_schema: Type[BaseModel]
    update_schema: Type[BaseModel]
    get_all_route: bool
    get_one_route: bool
    create_route: bool
    update_route: bool
    delete_one_route: bool
    delete_all_route: bool


class CRUDTemplate(APIRouter):
    schema: Type[BaseModel]
    create_schema: Type[BaseModel]
    update_schema: Type[BaseModel]
    _base_path: str = "/"

    def __init__(
            self,
            context: Context,
            **kwargs: Any,
    ) -> None:

        super().__init__(**kwargs)

        self.ctx = context
        self.schema = self.ctx['schema']
        self.create_schema = self.ctx['create_schema']
        self.update_schema  = self.ctx['update_schema']
        self.manager = self.ctx['manager']
        self.get_session = self.ctx['get_session']
        if self.ctx.get('get_all_route', True):
            self._get_all()

        if self.ctx.get('create_route', True):
            self._create()

        if self.ctx.get('get_one_route', True):
            self._get_one()

        if self.ctx.get('update_route', True):
            self._update()

        if self.ctx.get('delete_one_route', True):
            self._delete_one()

        if self.ctx.get('delete_all_route', True):
            self._delete_all()

    def api_route(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

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
