from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from ..database import Base


class Party(Base):
    __tablename__ = "party"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str]
    full_name: Mapped[str]
    short_name: Mapped[str]
