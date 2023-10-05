from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Parliament(Base):
    __tablename__ = "parliament"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    abgeordnetenwatch_url: Mapped[str] = mapped_column(String, nullable=False)
    label_long: Mapped[str] = mapped_column(String, nullable=False)
    last_election_id: Mapped[int] = mapped_column(Integer, ForeignKey("election.id"))

    election = relationship("Election", back_populates="parliament")
