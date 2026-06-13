from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    item_type: Mapped[str] = mapped_column(String, index=True)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)

    strength_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    agility_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    luck_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id"))

    owner = relationship("Character", back_populates="items")