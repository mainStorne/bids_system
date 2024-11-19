from fastapi import APIRouter
from .endpoints import users, auth, roles, files

api = APIRouter()
api.include_router(users.r, prefix='/users', tags=['users'])
api.include_router(auth.r, prefix='/auth/jwt', tags=['auth'])
api.include_router(roles.r, prefix='/roles', tags=['roles'])
api.include_router(files.r, prefix='/files', tags=['files'])
