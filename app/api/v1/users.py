from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = models.User(name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[schemas.User])
async def get_users(
    name_contains: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of users to return"),
    offset: int = Query(default=0, ge=0, description="Number of users to skip"),
    db: AsyncSession = Depends(get_db)
):
    query = select(models.User)

    # Фильтр по имени
    if name_contains:
        query = query.where(models.User.name.ilike(f"%{name_contains}%"))

    # Сортировка
    if sort:
        if sort.lstrip("-") == "items_count":
            query = query.outerjoin(models.User.characters).outerjoin(models.Character.items).group_by(models.User.id)
            count_func = func.count(models.Item.id)
            query = query.order_by(count_func.desc() if sort.startswith("-") else count_func.asc())
        else:
            column = getattr(models.User, sort.lstrip("-"))
            query = query.order_by(column.desc() if sort.startswith("-") else column.asc())

    # Пагинация
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)

    return result.scalars().unique().all()

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(models.User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(models.User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users(
    from_id: int = Query(..., alias="from"),
    to_id: int = Query(..., alias="to"),
    db: AsyncSession = Depends(get_db)
):
    if from_id > to_id:
        from_id, to_id = to_id, from_id

    req = delete(models.User).where(
        models.User.id >= from_id,
        models.User.id <= to_id
    )

    result = await db.execute(req)

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Users not found")

    await db.commit()


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, updated_user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await db.get(models.User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = updated_user.name
    await db.commit()
    await db.refresh(user)

    return user

@router.get("/{user_id}/characters", response_model=list[schemas.Character])
async def get_users_characters(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(models.User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = select(models.Character).where(models.Character.user_id == user_id)

    result = await db.execute(query)

    return result.scalars().unique().all()

