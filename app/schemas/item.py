from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str
    item_type: str = Field(..., example="weapon")
    
    strength_bonus: int = 0
    agility_bonus: int = 0
    luck_bonus: int = 0

    character_id: int

class Item(BaseModel):
    id: int
    name: str
    item_type: str
    
    strength_bonus: int
    agility_bonus: int
    luck_bonus: int

    is_equipped: bool
    character_id: int

    class Config:
        from_attributes = True