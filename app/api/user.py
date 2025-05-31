from fastapi import APIRouter

from app.core.users import fastapi_users
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()

# Include user management routes (current user, update profile, etc.)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
