from sys import prefix

from fastapi import APIRouter
from .endpoints import users, auth

api = APIRouter()
api.include_router(users.r, prefix='/users', tags=['users'])
api.include_router(auth.r, prefix='/auth/jwt', tags=['auth'])
