from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app import models, schemas

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[schemas.User])
def get_users(
    name_contains: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of users to return"),
    offset: int = Query(default=0, ge=0, description="Number of users to skip"),
    db: Session = Depends(get_db)
):
    query = db.query(models.User)

    # Фильтр по имени
    if name_contains:
        query = query.filter(models.User.name.ilike(f"%{name_contains}%"))

    # Сортировка
    if sort:
        if sort.lstrip("-") == "items_count":
            query = query.outerjoin(models.User.items).group_by(models.User.id)
            if sort.startswith("-"):
                query = query.order_by(func.count(models.Item.id).desc())
            else:
                query = query.order_by(func.count(models.Item.id).asc())
        else:
            if sort.startswith("-"):
                query = query.order_by(getattr(models.User, sort[1:]).desc())
            else:
                query = query.order_by(getattr(models.User, sort).asc())

    # Пагинация
    query = query.offset(offset).limit(limit)

    return query.all()

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, updated_user: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = updated_user.name
    db.commit()
    db.refresh(user)

    return user

@router.get("/{user_id}/items", response_model=list[schemas.Item])
def get_user_items(
    user_id: int,
    name_contains: str | None = Query(default=None, description="Filter items containing this string in name"),
    sort: str | None = Query(default=None, description="Sort by field, e.g., 'name', '-name'"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(models.Item).filter(models.Item.owner_id == user_id)

    # Фильтр по имени
    if name_contains:
        query = query.filter(models.Item.name.ilike(f"%{name_contains}%"))

    # Сортировка
    if sort:
        if sort.startswith("-"):
            query = query.order_by(getattr(models.Item, sort[1:]).desc())
        else:
            query = query.order_by(getattr(models.Item, sort).asc())

    # Пагинация
    query = query.offset(offset).limit(limit)

    return query.all()