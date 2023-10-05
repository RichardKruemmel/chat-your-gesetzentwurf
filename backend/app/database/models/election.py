from sqlalchemy import Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from ..database import Base


class Election(Base):
    __tablename__ = "election"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str]
    previous_election_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("election.id")
    )
    election_date: Mapped[Date]
    start_date_period: Mapped[Date]
    end_date_period: Mapped[Date]
    parliament_id: Mapped[int] = mapped_column(Integer, ForeignKey("parliament.id"))

    parliament = relationship("Parliament", back_populates="election")
    previous_election = relationship(
        "Election", remote_side=[id], backref=backref("next_election", uselist=False)
    )
