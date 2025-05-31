from uuid import UUID

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, CookieTransport
from fastapi_users.authentication.strategy import JWTStrategy

from app.core.config import settings
from app.models.user import User, get_user_manager

# Cookie transport for web-based authentication
cookie_transport = CookieTransport(cookie_name="auth", cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])
