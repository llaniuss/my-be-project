from pydantic import BaseModel, Field

class Monster(BaseModel):
    id: int
    name: str
    level: int
    hp: int
    strength: int
    agility: int
    luck: int
    exp_reward: int

    class Config:
        from_attributes = True

class MonsterCreate(BaseModel):
    name: str
    level: int
    hp: int
    strength: int
    agility: int
    luck: int
    exp_reward: int