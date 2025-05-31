from typing import Optional

import sqlalchemy.sql.functions
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
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
    count_query = select(sqlalchemy.sql.functions.count()).select_from(query.subquery())
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

    # Calculate display values for pagination
    start_item = ((page - 1) * per_page) + 1 if total > 0 else 0
    end_item = min(page * per_page, total)

    # Calculate page range for pagination links
    page_range_start = max(1, page - 2)
    page_range_end = min(total_pages + 1, page + 3)

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
        "start_item": start_item,
        "end_item": end_item,
        "page_range_start": page_range_start,
        "page_range_end": page_range_end,
        "user": user,
    }

    if htmx:
        return templates.TemplateResponse("items/_table.jinja2", context)

    return templates.TemplateResponse("items/index.jinja2", context)


@router.post("", response_class=HTMLResponse, name="create_item")
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

    # Get current search and pagination context
    search = request.query_params.get("search")
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 10))

    # Recalculate the items list and pagination after creation
    query = select(Item).where(Item.owner_id == user.id)
    if search:
        query = query.where(Item.title.ilike(f"%{search}%"))

    # Get updated total count
    count_query = select(sqlalchemy.sql.functions.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Calculate updated pagination info
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    # For new items, we typically want to show the first page where the item appears
    # Since items are usually ordered by creation time (newest first), go to page 1
    page = 1

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query for updated items
    result = await db.execute(query)
    items = result.scalars().all()

    # Calculate pagination display values
    has_prev = page > 1
    has_next = page < total_pages
    start_item = ((page - 1) * per_page) + 1 if total > 0 else 0
    end_item = min(page * per_page, total)
    page_range_start = max(1, page - 2)
    page_range_end = min(total_pages + 1, page + 3)

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
        "start_item": start_item,
        "end_item": end_item,
        "page_range_start": page_range_start,
        "page_range_end": page_range_end,
        "current_user": user,
    }

    # Return updated table
    return templates.TemplateResponse("items/_table.jinja2", context)


@router.get("/{item_id}/edit", response_class=HTMLResponse, name="get_edit_item_form")
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


@router.put("/{item_id}", response_class=HTMLResponse, name="update_item")
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

    # Get pagination context from query params for consistency
    search = request.query_params.get("search", "")
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 10))

    # Return updated item row with pagination context
    return templates.TemplateResponse(
        "items/_item_row.jinja2",
        {
            "request": request,
            "item": item,
            "current_user": user,
            "search": search,
            "page": page,
            "per_page": per_page,
        },
    )


@router.delete("/{item_id}", response_class=HTMLResponse, name="delete_item")
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

    # Get current page and search from query params to maintain state
    search = request.query_params.get("search")
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 10))

    # Recalculate the items list and pagination after deletion
    query = select(Item).where(Item.owner_id == user.id)
    if search:
        query = query.where(Item.title.ilike(f"%{search}%"))

    # Get updated total count
    count_query = select(sqlalchemy.sql.functions.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Calculate updated pagination info
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    # If current page is now beyond the total pages, go to the last page
    if page > total_pages and total_pages > 0:
        page = total_pages

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    # Execute query for updated items
    result = await db.execute(query)
    items = result.scalars().all()

    # Calculate pagination display values
    has_prev = page > 1
    has_next = page < total_pages
    start_item = ((page - 1) * per_page) + 1 if total > 0 else 0
    end_item = min(page * per_page, total)
    page_range_start = max(1, page - 2)
    page_range_end = min(total_pages + 1, page + 3)

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
        "start_item": start_item,
        "end_item": end_item,
        "page_range_start": page_range_start,
        "page_range_end": page_range_end,
        "current_user": user,
    }

    # Return updated table
    return templates.TemplateResponse("items/_table.jinja2", context)


@router.get("/{item_id}/cancel", response_class=HTMLResponse, name="cancel_edit_item")
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

    # Get pagination context from query params for consistency
    search = request.query_params.get("search", "")
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 10))

    # Return the item row in view mode with pagination context
    return templates.TemplateResponse(
        "items/_item_row.jinja2",
        {
            "request": request,
            "item": item,
            "current_user": user,
            "search": search,
            "page": page,
            "per_page": per_page,
        },
    )
