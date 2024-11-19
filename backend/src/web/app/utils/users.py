from fastapi_users.authentication.backend import AuthenticationBackend
from ..authentication.transport import BearerTransport
from ..authentication.authenticator import Authenticator
from ..authentication.strategy import JWTStrategy
from ..conf import settings
from ..managers.users import UsersManager
from ..dependencies.session import get_session

transport = BearerTransport('auth/jwt/login', scopes={'costumer': 'request bids'})


def get_strategy():
    return JWTStrategy(secret=settings.JWT_PRIVATE_KEY, lifetime_seconds=None)


backend = AuthenticationBackend(name='jwt', get_strategy=get_strategy, transport=transport)
user_manager = UsersManager()

authenticator = Authenticator([backend], get_session)
