from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users.password import PasswordHelper
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.templates import templates
from app.core.users import fastapi_users
from app.models.user import User, UserManager, get_user_manager
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


# Custom profile page endpoint
@router.get("/profile", response_class=HTMLResponse, name="user_profile")
async def get_profile_page(
    request: Request,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Get user profile page with full user data including items."""

    # Load user with items for statistics
    result = await db.execute(
        select(User).options(selectinload(User.items)).where(User.id == user.id)  # type: ignore[arg-type]
    )
    user_with_items = result.scalar_one()

    return templates.TemplateResponse(
        "profile.jinja2",
        {"request": request, "user": user_with_items},
    )


# Profile update endpoints
@router.patch("/profile/email", response_class=HTMLResponse, name="update_user_email")
async def update_email(
    email_data: dict[str, Any],
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Update user email."""

    try:
        # Check if email is already taken
        existing_user = await db.execute(
            select(User).where(
                and_(User.email == email_data["email"], User.id != user.id)  # type: ignore[arg-type]
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Update email
        user.email = email_data["email"]
        await db.commit()

        # Return updated email display
        email_html = f"""
            <div id="email-display"
                 class="bg-gray-50 px-3 py-2 rounded-md border
                        flex justify-between items-center">
                <span class="text-gray-800">{user.email}</span>
                <button onclick="editField('email', '{user.email}')"
                        class="text-blue-600 hover:text-blue-800 text-sm">
                    Edit
                </button>
            </div>
            """
        return HTMLResponse(content=email_html, status_code=200)
    except HTTPException:
        raise
    except (ValueError, KeyError) as e:
        error_html = f"""
            <div class="bg-red-50 border border-red-200 text-red-700
                        px-4 py-3 rounded">
                Error updating email: {str(e)}
            </div>
            """
        return HTMLResponse(content=error_html, status_code=400)


@router.patch(
    "/profile/password",
    response_class=HTMLResponse,
    name="update_user_password",
)
async def update_password(
    password_data: dict[str, Any],
    user: User = Depends(fastapi_users.current_user(active=True)),
    user_manager: UserManager = Depends(get_user_manager),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Update user password."""

    try:
        # Validate password confirmation
        if password_data.get("password") != password_data.get("confirm_password"):
            error_html = """
                <div class="bg-red-50 border border-red-200 text-red-700
                            px-4 py-3 rounded">
                    Passwords do not match
                </div>
                """
            return HTMLResponse(content=error_html, status_code=400)

        current_password = password_data.get("current_password")
        new_password = password_data.get("password")

        if not current_password or not new_password:
            error_html = """
                <div class="bg-red-50 border border-red-200 text-red-700
                            px-4 py-3 rounded">
                    Current password and new password are required
                </div>
                """
            return HTMLResponse(content=error_html, status_code=400)

        # Verify current password
        password_helper = PasswordHelper()
        is_valid = password_helper.verify_and_update(
            current_password,
            user.hashed_password,
        )[0]

        if not is_valid:
            error_html = """
                <div class="bg-red-50 border border-red-200 text-red-700
                            px-4 py-3 rounded">
                    Current password is incorrect
                </div>
                """
            return HTMLResponse(content=error_html, status_code=400)

        # Validate new password (using UserManager's password validation)
        try:
            await user_manager.validate_password(new_password, user)
        except InvalidPasswordException as e:
            error_html = f"""
                <div class="bg-red-50 border border-red-200 text-red-700
                            px-4 py-3 rounded">
                    Password validation failed: {str(e)}
                </div>
                """
            return HTMLResponse(content=error_html, status_code=400)

        # Hash and update password
        hashed_password = password_helper.hash(new_password)
        user.hashed_password = hashed_password
        await db.commit()

        success_html = """
            <div class="bg-green-50 border border-green-200 text-green-700
                        px-4 py-3 rounded">
                Password updated successfully!
            </div>
            """
        return HTMLResponse(content=success_html, status_code=200)
    except InvalidPasswordException:
        raise
    except (ValueError, KeyError) as e:
        error_html = f"""
            <div class="bg-red-50 border border-red-200 text-red-700
                        px-4 py-3 rounded">
                Error updating password: {str(e)}
            </div>
            """
        return HTMLResponse(content=error_html, status_code=400)


# Include the original FastAPI Users routes for API access
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
