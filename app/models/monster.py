from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class Monster(Base):
    __tablename__ = "monsters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    
    hp: Mapped[int] = mapped_column(Integer)
    strength: Mapped[int] = mapped_column(Integer)
    agility: Mapped[int] = mapped_column(Integer)
    luck: Mapped[int] = mapped_column(Integer)
    
    exp_reward: Mapped[int] = mapped_column(Integer)

    def get_stats(self):
        return {
            "hp": self.hp,
            "strength": self.strength,
            "agility": self.agility,
            "luck": self.luck
            }