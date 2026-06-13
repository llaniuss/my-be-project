from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/monsters", tags=["monsters"])

# CREATE
@router.post("/", response_model=schemas.Monster)
async def create_monster(monster: schemas.MonsterCreate, db: AsyncSession = Depends(get_db)):
    db_monster = models.Monster(**monster.model_dump())

    db.add(db_monster)

    await db.commit()
    await db.refresh(db_monster)

    return db_monster

# READ ALL
@router.get("/", response_model=list[schemas.Monster])
async def get_monsters(
    db: AsyncSession = Depends(get_db)
):
    query = select(models.Monster)

    result = await db.execute(query)

    return result.scalars().unique().all()

# DELETE
@router.delete("/{monster_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monster(monster_id: int, db: AsyncSession = Depends(get_db)):
    monster = await db.get(models.Monster, monster_id)
    if monster is None:
        raise HTTPException(status_code=404, detail="Monster not found")
    await db.delete(monster)
    await db.commit()