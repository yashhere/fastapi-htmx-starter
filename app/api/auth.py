from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.templates import templates
from app.core.users import fastapi_users
from app.models.user import User

router: APIRouter = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse, name="auth_login_page")
async def get_login_page(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> Response:
    if user:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("auth/login.jinja2", {"request": request})


@router.get("/register", response_class=HTMLResponse, name="auth_register_page")
async def get_register_page(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> Response:
    if user:
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("auth/register.jinja2", {"request": request})


@router.get("/logout", response_class=RedirectResponse, name="auth_logout_redirect")
async def logout_redirect() -> RedirectResponse:
    """Redirect to the cookie logout endpoint."""
    return RedirectResponse(url="/auth/cookie/logout", status_code=302)
