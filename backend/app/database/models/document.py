from sqlalchemy import String, Date, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Document(Base):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    label: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[Date] = mapped_column(Date)
    pdf_data: Mapped[LargeBinary] = mapped_column(LargeBinary)
