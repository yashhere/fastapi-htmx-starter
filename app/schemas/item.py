from uuid import UUID

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class ItemRead(ItemBase):
    id: int
    owner_id: UUID

    class Config:
        from_attributes = True
