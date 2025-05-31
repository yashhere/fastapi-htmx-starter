import logging
from datetime import datetime
from typing import TYPE_CHECKING, AsyncGenerator, List
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users.db import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base, get_db

if TYPE_CHECKING:
    from app.models.item import Item

logger = logging.getLogger(__name__)


class User(SQLAlchemyBaseUserTableUUID, Base):
    # fastapi-users provides: id, email, hashed_password, is_active,
    # is_superuser, is_verified. Add any custom fields specific to your
    # application here, for example:
    # first_name: Mapped[str | None] = mapped_column(String(length=50))
    # last_name: Mapped[str | None] = mapped_column(String(length=50))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="owner",
    )


async def get_user_db(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(
        self,
        user: User,
        request: Request | None = None,
    ) -> None:
        logger.info("User %s (%s) has registered successfully.", user.id, user.email)

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ) -> None:
        logger.info("User %s (%s) requested password reset.", user.id, user.email)

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ) -> None:
        logger.info("Verification requested for user %s (%s).", user.id, user.email)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Get user manager dependency."""
    yield UserManager(user_db)
