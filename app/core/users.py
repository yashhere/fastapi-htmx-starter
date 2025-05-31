from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTAuthentication,
)

from app.core.config import settings
from app.models.user import User, get_user_manager

# Cookie transport for web-based authentication
cookie_transport = CookieTransport(cookie_name="auth", cookie_max_age=3600)

# JWT authentication
jwt_authentication = JWTAuthentication(
    secret=settings.SECRET_KEY,
    lifetime_seconds=3600,
)

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=lambda: jwt_authentication,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
