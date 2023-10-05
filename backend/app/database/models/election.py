from sqlalchemy import Integer, String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from ..database import Base


class Election(Base):
    __tablename__ = "election"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] =  mapped_column(String, nullable=False)
    previous_election_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("election.id")
    )
    election_date: Mapped[Date] =  mapped_column(Date, nullable=False)
    start_date_period: Mapped[Date] =  mapped_column(Date, nullable=False)
    end_date_period: Mapped[Date] =  mapped_column(Date, nullable=False)
    parliament_id: Mapped[int] = mapped_column(Integer, ForeignKey("parliament.id"), nullable=False)

    parliament = relationship("Parliament", back_populates="election")
    previous_election = relationship(
        "Election", remote_side=[id], backref=backref("next_election", uselist=False)
    )
    election_programs = relationship("ElectionProgram", back_populates="parliament_period")