import logging
from pathlib import Path
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# Import routers
from app.api import auth as auth_api_router
from app.api import items as items_api_router
from app.api import user as user_api_router
from app.api.dependencies import is_htmx
from app.core.config import settings
from app.core.database import init_db
from app.core.templates import templates
from app.core.users import auth_backend, fastapi_users
from app.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    # Log startup information (server logs only, not web pages)
    key_start = settings.SECRET_KEY[: min(len(settings.SECRET_KEY), 8)]
    logger.info("Starting FastAPI HTMX Starter application")
    logger.info("Using SECRET_KEY starting with: %s...", key_start)
    logger.info(
        "Ensure SECRET_KEY is set persistently in your .env file "
        "for sessions to work across restarts.",
    )

    await init_db()
    yield


app = FastAPI(title="FastAPI HTMX Starter", lifespan=lifespan)
app.add_middleware(GZipMiddleware)

# Determine the base directory relative to this file
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Auth routes (login, logout) - using the chosen backend (cookie in this case)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/cookie",
    tags=["auth"],
)

# User management routes (CRUD) - e.g., /users/me
app.include_router(user_api_router.router)

# Custom HTML-serving auth routes and custom /register endpoint
app.include_router(auth_api_router.router, prefix="/auth")

# Items CRUD routes
app.include_router(
    items_api_router.router,
    prefix="/items",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    """
    Custom exception handler to manage HTTPExceptions.
    - For 401 Unauthorized:
        - HTMX requests: Returns HX-Redirect header to the login page.
        - Non-HTMX requests: Returns a standard 302 redirect to the login page.
    - For other HTTPExceptions: Returns the default JSON response.
    """

    if exc.status_code == 401:
        login_url = request.url_for("auth_login_page")
        if is_htmx(request):
            # For HTMX requests resulting in 401, trigger a client-side redirect
            # via HX-Redirect header.
            return Response(
                content="",
                status_code=200,  # 200 is often used with HX-Redirect
                headers={"HX-Redirect": str(login_url)},
            )
        else:
            # For non-HTMX requests (e.g., full page loads), perform a standard
            # server-side redirect to the login page.
            return RedirectResponse(url=str(login_url), status_code=302)

    # For all other HTTPExceptions (not 401), return the default JSON response
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(
            exc,
            "headers",
            None,
        ),
    )


@app.get("/")
async def index(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.jinja2",
        {"request": request, "user": user},
    )
