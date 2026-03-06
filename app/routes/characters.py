from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post("/", response_model=schemas.Character)
async def create_character(
    character: schemas.CharCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(models.User, character.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_character = models.Character(
        name=character.name,
        level=character.level,
        health=character.health,
        exp=character.exp,
        user_id=character.user_id
        )
    
    db.add(db_character)

    await db.commit()
    await db.refresh(db_character)

    return db_character

# READ ALL
@router.get("/", response_model=list[schemas.Character])
async def get_characters(
    user_id: int | None = Query(default=None, description="Filter characters by user"),
    name_contains: str | None = Query(default=None, description="Filter by substring in name"),
    sort: str | None = Query(default=None, description="Sort by field, e.g. 'name' or '-level'"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(models.Character)

    # Фильтр по пользователю
    if user_id is not None:
        query = query.where(models.Character.user_id == user_id)

    # Фильтр по имени
    if name_contains:
        query = query.where(models.Character.name.ilike(f"%{name_contains}%"))

    # Сортировка
    if sort:
        field = sort.lstrip("-")
        if not hasattr(models.Character, field):
            raise HTTPException(status_code=400, detail="Invalid sort field")
        column = getattr(models.Character, field)
        query = query.order_by(column.desc() if sort.startswith("-") else column.asc())

    query = query.offset(offset).limit(limit)

    result = await db.execute(query) 
    return result.scalars().unique().all()


# READ ONE
@router.get("/{character_id}", response_model=schemas.Character)
async def get_character(character_id: int, db: AsyncSession = Depends(get_db)):
    character = await db.get(models.Character, character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return character


# UPDATE
@router.put("/{character_id}", response_model=schemas.Character)
async def update_character(
    character_id: int,
    updated_character: schemas.CharUpdate,
    db: AsyncSession = Depends(get_db)
):
    character = await db.get(models.Character, character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Если хотим позволять менять только имя и stats
    if updated_character.name is not None:
        character.name = updated_character.name
    if updated_character.level is not None:
        character.level = updated_character.level
    if updated_character.health is not None:
        character.health = updated_character.health
    if updated_character.exp is not None:
        character.exp = updated_character.exp

    await db.commit()
    await db.refresh(character)
    return character

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: int, db: AsyncSession = Depends(get_db)):
    character = await db.get(models.Character, character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    await db.delete(character)
    await db.commit()

@router.get("/{character_id}/items", response_model=list[schemas.Item])
async def get_character_items(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    character = await db.get(models.Character, character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    query = select(models.Item).where(models.Item.character_id == character_id)

    result = await db.execute(query)

    return result.scalars().unique().all()

@router.get("/{character_id}/user", response_model=schemas.User)
async def get_character_user(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    character = await db.get(models.Character, character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    user = await db.get(models.User, character.user_id)

    return user