from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str


class User(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ItemCreate(BaseModel):
    name: str
    character_id: int

class Item(BaseModel):
    id: int
    name: str
    character_id: int

    class Config:
        from_attributes = True

class CharCreate(BaseModel):
    name: str
    
    level: int
    health: int
    exp: int

    user_id: int

class CharUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    health: Optional[int] = None
    exp: Optional[int] = None

class Character(BaseModel):
    id: int
    name: str
    
    level: int
    health: int
    exp: int

    user_id: int
    
    class Config:
        from_attributes = True