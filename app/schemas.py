from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str


class User(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ItemCreate(BaseModel):
    name: str
    owner_id: int

class Item(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True