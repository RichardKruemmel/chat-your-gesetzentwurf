from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ElectionProgram(Base):
    __tablename__ = "election_program"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    election_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("election.id"), index=True, unique=True, nullable=False
    )
    party_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("party.id"), nullable=False
    )
    abgeordnetenwatch_file_url: Mapped[str] = mapped_column(String, nullable=False)
    file_cloud_url: Mapped[str] = mapped_column(String)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id"), index=True, unique=True
    )

    election = relationship("Election", back_populates="election_programs")
    party = relationship("Party", back_populates="election_programs")
    document = relationship(
        "Document", uselist=False, back_populates="election_program"
    )
