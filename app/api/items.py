from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import is_htmx
from app.core.database import get_db
from app.core.templates import templates
from app.core.users import fastapi_users
from app.models.item import Item
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate

router = APIRouter(tags=["items"])


@router.get("", response_class=HTMLResponse, name="list_items")
async def list_items(
    request: Request,
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    htmx: bool = Depends(is_htmx),
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """List items with search and pagination."""

    # Build query
    query = select(Item).where(Item.owner_id == user.id)

    if search:
        query = query.where(Item.title.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()

    # Calculate pagination info
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    context = {
        "request": request,
        "items": items,
        "search": search or "",
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "current_user": user,
    }

    if htmx:
        return templates.TemplateResponse("items/_table.jinja2", context)

    return templates.TemplateResponse("items/index.jinja2", context)


@router.post("", response_class=HTMLResponse)
async def create_item(
    request: Request,
    item_data: ItemCreate,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Create a new item."""

    item = Item(
        title=item_data.title,
        description=item_data.description,
        owner_id=user.id,
    )

    db.add(item)
    await db.commit()
    await db.refresh(item)

    # Return the new item row
    return templates.TemplateResponse(
        "items/_item_row.jinja2",
        {"request": request, "item": item, "current_user": user},
    )


@router.get("/{item_id}/edit", response_class=HTMLResponse)
async def get_edit_item_form(
    request: Request,
    item_id: int,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Get edit form for an item."""

    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id),
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return templates.TemplateResponse(
        "items/_edit_form.jinja2",
        {"request": request, "item": item},
    )


@router.put("/{item_id}", response_class=HTMLResponse)
async def update_item(
    request: Request,
    item_id: int,
    item_data: ItemUpdate,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Update an item."""

    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id),
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update fields
    if item_data.title is not None:
        item.title = item_data.title
    if item_data.description is not None:
        item.description = item_data.description

    await db.commit()
    await db.refresh(item)

    # Return updated item row
    return templates.TemplateResponse(
        "items/_item_row.jinja2",
        {"request": request, "item": item, "current_user": user},
    )


@router.delete("/{item_id}", response_class=HTMLResponse)
async def delete_item(
    request: Request,
    item_id: int,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Delete an item."""

    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id),
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()

    # Return empty response (item row will be removed by HTMX)
    return HTMLResponse(content="", status_code=200)


@router.get("/{item_id}/cancel", response_class=HTMLResponse)
async def cancel_edit_item(
    request: Request,
    item_id: int,
    user: User = Depends(fastapi_users.current_user(active=True)),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """Cancel editing an item and return to view mode."""

    result = await db.execute(
        select(Item).where(Item.id == item_id, Item.owner_id == user.id),
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Return the item row in view mode
    return templates.TemplateResponse(
        "items/_item_row.jinja2",
        {"request": request, "item": item, "current_user": user},
    )
