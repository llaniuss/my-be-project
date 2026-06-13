from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, delete, func
from random import randint

from app.database import get_db
from app import models, schemas, services

router = APIRouter(prefix="/characters", tags=["characters"])

@router.post("/", response_model=schemas.Character)
async def create_character(
    character: schemas.CharCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(models.User, character.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_character = models.Character(**character.model_dump())
    
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
    query = select(models.Character).options(selectinload(models.Character.items))

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
    query = (
        select(models.Character)
        .where(models.Character.id == character_id)
        .options(selectinload(models.Character.items))
    )
    result = await db.execute(query)
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return character


# UPDATE
@router.patch("/{character_id}", response_model=schemas.Character)
async def update_character(
    character_id: int,
    data: schemas.CharUpdate,
    db: AsyncSession = Depends(get_db)
):
    character = await db.get(models.Character, character_id)

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(character, key, value)

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

@router.post("/{character_id}/regenerate", response_model=schemas.Character)
async def regeneration(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = (select(models.Character).where(models.Character.id == character_id).options(selectinload(models.Character.items)))
    result = await db.execute(query)
    character = result.scalar_one()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character.health = character.max_health

    db.add(character)

    await db.commit()
    await db.refresh(character)

    return character

@router.post("/{character_id}/gain_xp", response_model=schemas.Character)
async def gain_experience(
    character_id: int,
    data: schemas.ExperienceGain,
    db: AsyncSession = Depends(get_db)
):
    query = (select(models.Character).where(models.Character.id == character_id).options(selectinload(models.Character.items)))
    result = await db.execute(query)
    character = result.scalar_one()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    result = services.gain_xp(character.exp, data.exp, character.level, character.attribute_points)

    character.exp = result["exp"]
    character.level = result["level"]
    character.attribute_points = result["ap"]
    if result["hp"] != None:
        character.health = result["hp"]
    
    db.add(character)

    await db.commit()
    await db.refresh(character)

    return character

@router.post("/{character_id}/spend_points", response_model=schemas.Character)
async def spend_points(
    character_id: int,
    data: schemas.AttributeAssign,
    db: AsyncSession = Depends(get_db)
):
    query = (select(models.Character).where(models.Character.id == character_id).options(selectinload(models.Character.items)))
    result = await db.execute(query)
    character = result.scalar_one()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    if character.attribute_points < data.amount:
        raise HTTPException(status_code=400, detail="Not enough points")
    
    attr_name = data.attribute.lower()
    
    match attr_name:
        case "strength":
            character.strength += data.amount
        case "agility":
            character.agility += data.amount
        case "intelligence":
            character.intelligence += data.amount
        case "luck":
            character.luck += data.amount
        case _:
            raise HTTPException(status_code=400, detail=f'No attribute "{attr_name}".')
        

    character.attribute_points -= data.amount
    
    db.add(character)

    await db.commit()
    await db.refresh(character)

    return character

@router.post("/battle")
async def let_em_fight(
    data: schemas.BattleRequest,
    db: AsyncSession = Depends(get_db)
):
    att_query = (
        select(models.Character)
        .where(models.Character.id == data.attacker_id)
        .options(selectinload(models.Character.items))
    )
    result1 = await db.execute(att_query)
    attacker = result1.scalar_one_or_none()
    
    def_query = (
        select(models.Character)
        .where(models.Character.id == data.defender_id)
        .options(selectinload(models.Character.items))
    )
    result2 = await db.execute(def_query)
    defender = result2.scalar_one_or_none()

    damage = services.calculate_damage(attacker.total_strength, attacker.total_luck, defender.total_agility)
    defender.health -= damage
    is_killed = defender.health <= 0
    
    db.add(attacker)
    db.add(defender)

    await db.commit()
    await db.refresh(attacker)
    await db.refresh(defender)

    return f"{attacker.name} hit {defender.name}. {defender.name} was damaged by {damage} hp. {defender.name} {'was' if is_killed else 'was not'} killed."

@router.post("/{character_id}/adventure", response_model=schemas.BattleResponse)
async def adventure(
    character_id: int,
    db: AsyncSession = Depends(get_db)
    ):
    char_query = (
        select(models.Character)
        .where(models.Character.id == character_id)
        .options(selectinload(models.Character.items))
    )
    result1 = await db.execute(char_query)
    character = result1.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    mon_query = (select(models.Monster).where(models.Monster.level <= character.level).order_by(models.Monster.level.desc()).limit(1))
    result2 = await db.execute(mon_query)
    monster = result2.scalar_one_or_none()

    if not monster:
        raise HTTPException(status_code=404, detail="No suitable monsters found for your level")

    logs = []

    logs.append(f"Character {character.name} met {monster.name}!")

    
    battle = services.resolve_battle(character.get_stats(), monster.get_stats())

    for log in battle["logs"]:
        if log["is_attacker"]:
            logs.append(f"{character.name} hit {monster.name} and damaged him by {log['dmg']} hp.")
        else:
            logs.append(f"{monster.name} hit {character.name} and damaged him by {log['dmg']} hp.")

    if battle["winner"]:
        result = services.gain_xp(character.exp, monster.exp_reward, character.level, character.attribute_points)

        character.exp = result["exp"]
        character.level = result["level"]
        character.attribute_points = result["ap"]
        character.health = result["hp"] if result["hp"] else battle["att_final_hp"]
        logs.append(f"{character.name} defeated {monster.name} and received {monster.exp_reward} xp!")
    else:
        character.health = character.max_health // 2
        character.exp = int(character.exp * 0.9)
        logs.append(f"{character.name} was defeated by {monster.name}. Rest in peace.")
    
    db.add(character)

    await db.commit()
    await db.refresh(character)

    return {"logs": logs, "character": character}


    





