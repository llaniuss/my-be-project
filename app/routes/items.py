from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/items", tags=["items"])

# CREATE
@router.post("/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(name=item.name, owner_id=item.owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# READ ALL
@router.get("/", response_model=list[schemas.Item])
def get_items(
    owner_id: int | None = Query(default=None),
    name_contains: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(models.Item)

    # Фильтр по owner
    if owner_id is not None:
        query = query.filter(models.Item.owner_id == owner_id)

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

# READ ONE
@router.get("/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# UPDATE
@router.put("/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, updated_item: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = updated_item.name
    item.owner_id = updated_item.owner_id
    db.commit()
    db.refresh(item)
    return item

# DELETE
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

# READ USERS' ITEMS
@router.get("/by_user/{user_id}", response_model=list[schemas.Item])
def get_items_by_user(
    user_id: int,
    name_contains: str | None = Query(default=None, description="Filter items containing this string in name"),
    sort: str | None = Query(default=None, description="Sort by field, e.g. 'name' or '-name'"),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(models.Item).filter(models.Item.owner_id == user_id)

    # Фильтр по имени
    if name_contains:
        query = query.filter(models.Item.name.ilike(f"%{name_contains}%"))

    # Сортировка
    if sort:
        if sort.startswith("-"):
            field_name = sort[1:]
            query = query.order_by(getattr(models.Item, field_name).desc())
        else:
            query = query.order_by(getattr(models.Item, sort).asc())

    return query.all()