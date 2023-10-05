from sqlalchemy import String, Date, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[Date] = mapped_column(Date)
    pdf_data: Mapped[LargeBinary] = mapped_column(LargeBinary)

    embeddings = relationship("Embedding", back_populates="document", uselist=False)
