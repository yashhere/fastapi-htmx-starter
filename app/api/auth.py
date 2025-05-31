import logging

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api.dependencies import is_htmx
from app.core.templates import templates
from app.core.users import fastapi_users
from app.models.user import User, UserManager, get_user_manager
from app.schemas.user import UserCreate

router: APIRouter = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse, name="auth_login_page")
async def get_login_page(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> Response:
    if user:
        return RedirectResponse(url=request.url_for("index"), status_code=302)

    return templates.TemplateResponse("auth/login.jinja2", {"request": request})


@router.get("/register", response_class=HTMLResponse, name="auth_register_page")
async def get_register_page(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> Response:
    if user:
        return RedirectResponse(url=request.url_for("index"), status_code=302)

    return templates.TemplateResponse("auth/register.jinja2", {"request": request})


@router.post("/register", name="auth_register")
async def register_user(
    request: Request,
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager),
) -> Response:
    """Custom registration endpoint that redirects to login after success."""
    try:
        # Create the user
        user = await user_manager.create(user_create, safe=True, request=request)
        logger.info("User %s registered successfully, redirecting to login", user.email)

        # Check if this is an HTMX request
        if is_htmx(request):
            # For HTMX requests, return an HX-Redirect header
            login_url = str(request.url_for("auth_login_page")) + "?registered=true"
            return Response(
                content="",
                status_code=200,
                headers={"HX-Redirect": login_url},
            )
        else:
            # For regular requests, return a standard redirect
            login_url = str(request.url_for("auth_login_page")) + "?registered=true"
            return RedirectResponse(url=login_url, status_code=302)

    except Exception as e:
        logger.error("Registration failed: %s", str(e))
        # Re-raise the exception to let FastAPI Users handle it properly
        # This will return the appropriate error response
        raise


@router.post("/logout", name="auth_logout")
async def logout_user(
    request: Request,
    user: User = Depends(fastapi_users.current_user()),
) -> Response:
    """Handle logout by making a request to the FastAPI Users logout endpoint."""
    logger.info("User %s logging out", user.email)

    # Check if this is an HTMX request
    if is_htmx(request):
        # For HTMX requests, return an HX-Redirect header to the home page
        # The cookie will be cleared by the FastAPI Users middleware
        return Response(
            content="",
            status_code=200,
            headers={
                "HX-Redirect": str(request.url_for("index")),
                "Set-Cookie": "auth=; Path=/; Max-Age=0; HttpOnly; SameSite=lax",
            },
        )
    else:
        # For regular requests, clear the cookie and redirect
        response = RedirectResponse(url=request.url_for("index"), status_code=302)
        response.set_cookie(
            key="auth",
            value="",
            max_age=0,
            httponly=True,
            samesite="lax",
        )
        return response
