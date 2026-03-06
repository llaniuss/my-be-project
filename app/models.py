from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    
    character = relationship("Character", back_populates="user", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id"))

    owner = relationship("Character", back_populates="items")


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    user = relationship("User", back_populates="character")