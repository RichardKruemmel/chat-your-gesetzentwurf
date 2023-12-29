from app.database.models.election import Election
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Parliament(Base):
    __tablename__ = "parliament"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    abgeordnetenwatch_url: Mapped[str] = mapped_column(String, nullable=False)
    label_long: Mapped[str] = mapped_column(String, nullable=False)
    last_election_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("election.id", use_alter=True)
    )

    elections = relationship(
        "Election",
        back_populates="parliament",
        post_update=True,
        foreign_keys=[Election.parliament_id],
    )
    last_election = relationship("Election", foreign_keys=[last_election_id])
