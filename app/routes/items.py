from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/items", tags=["items"])

# CREATE
@router.post("/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    character = await db.get(models.Character, item.character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    db_item = models.Item(
        name=item.name, 
        character_id=item.character_id
    )

    db.add(db_item)
    
    await db.commit()
    await db.refresh(db_item)

    return db_item

# READ ALL
@router.get("/", response_model=list[schemas.Item])
async def get_items(
    character_id: int | None = Query(default=None),
    name_contains: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(models.Item)

    # Фильтр по owner
    if character_id is not None:
        query = query.where(models.Item.character_id == character_id)

    # Фильтр по имени
    if name_contains:
        query = query.where(models.Item.name.ilike(f"%{name_contains}%"))

    # Сортировка
    if sort:
        field = sort.lstrip("-")
        if not hasattr(models.Item, field):
            raise HTTPException(status_code=400, detail="Invalid sort field")
        column = getattr(models.Item, field)
        query = query.order_by(column.desc() if sort.startswith("-") else column.asc())

    # Пагинация
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)

    return result.scalars().unique().all()

# READ ONE
@router.get("/{item_id}", response_model=schemas.Item)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(models.Item, item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

# UPDATE
@router.put("/{item_id}", response_model=schemas.Item)
async def update_item(
    item_id: int,
    updated_item: schemas.ItemCreate,
    db: AsyncSession = Depends(get_db)
):
    item = await db.get(models.Item, item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    character = await db.get(models.Character, updated_item.character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    item.name = updated_item.name
    item.character_id = updated_item.character_id

    await db.commit()
    await db.refresh(item)

    return item

# DELETE
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
    await db.commit()

# READ CHARACTERS' ITEMS
@router.get("/by_character/{character_id}", response_model=list[schemas.Item])
async def get_items_by_character(
    character_id: int,
    name_contains: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    character = await db.get(models.Character, character_id)

    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    query = select(models.Item).where(models.Item.character_id == character_id)

    if name_contains:
        query = query.where(models.Item.name.ilike(f"%{name_contains}%"))

    if sort:
        field = sort.lstrip("-")

        if not hasattr(models.Item, field):
            raise HTTPException(status_code=400, detail="Invalid sort field")

        column = getattr(models.Item, field)

        query = query.order_by(
            column.desc() if sort.startswith("-") else column.asc()
        )

    result = await db.execute(query)

    return result.scalars().unique().all()