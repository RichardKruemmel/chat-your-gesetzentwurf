from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Parliament(Base):
    __tablename__ = "parliament"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str]
    abgeordnetenwatch_url: Mapped[str]
    label_external_long: Mapped[str]
    last_election_id: Mapped[int] = mapped_column(Integer, ForeignKey("election.id"))

    election = relationship("Election", back_populates="parliament")
