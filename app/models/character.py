from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .item import Item

class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    exp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    strength: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    agility: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    luck: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    attribute_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
    user = relationship("User", back_populates="character")

    @property
    def max_health(self) -> int:
        return 80 + (self.level * 20)
    
    @property
    def total_strength(self) -> int:
        bonus = sum(item.strength_bonus for item in self.items if item.is_equipped)
        return self.strength + bonus
    
    @property
    def total_agility(self) -> int:
        bonus = sum(item.agility_bonus for item in self.items if item.is_equipped)
        return self.agility + bonus
    
    @property
    def total_luck(self) -> int:
        bonus = sum(item.luck_bonus for item in self.items if item.is_equipped)
        return self.luck + bonus
    
    def get_stats(self):
        return {
            "hp": self.health,
            "strength": self.total_strength,
            "agility": self.total_agility,
            "luck": self.total_luck
            }

