from pydantic import BaseModel, Field, computed_field
from typing import Optional
from .item import Item

class CharCreate(BaseModel):
    name: str
    
    level: int = Field(1)
    health: int = Field(100)
    exp: int = Field(0)

    strength: int = Field(10)
    agility: int = Field(10)
    luck: int = Field(10)

    attribute_points: int = Field(0)

    user_id: int

class CharUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    health: Optional[int] = None
    exp: Optional[int] = None
    strength: Optional[int] = None
    agility: Optional[int] = None
    luck: Optional[int] = None
    attribute_points: Optional[int] = None



class Character(BaseModel):
    id: int
    name: str
    
    level: int
    health: int
    exp: int

    strength: int
    agility: int
    luck: int

    attribute_points: int

    user_id: int

    items: list[Item] = [] 

    @computed_field
    @property
    def max_health(self) -> int:
        return 80 + (self.level * 20)

    @computed_field
    @property
    def total_strength(self) -> int:
        bonus = sum(item.strength_bonus for item in self.items if item.is_equipped)
        return self.strength + bonus
    
    @computed_field
    @property
    def total_agility(self) -> int:
        bonus = sum(item.agility_bonus for item in self.items if item.is_equipped)
        return self.agility + bonus
    
    @computed_field
    @property
    def total_luck(self) -> int:
        bonus = sum(item.luck_bonus for item in self.items if item.is_equipped)
        return self.luck + bonus
    
    class Config:
        from_attributes = True

class ExperienceGain(BaseModel):
    exp: int

class AttributeAssign(BaseModel):
    attribute: str = Field("strength")
    amount: int = Field(gt=0)

class BattleRequest(BaseModel):
    attacker_id: int
    defender_id: int

class BattleResponse(BaseModel):
    logs: list[str]
    character: Character