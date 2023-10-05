from sqlalchemy import Column, String, Integer

from ..database import Base


class Party(Base):
    __tablename__ = "party"

    id = Column(Integer, primary_key=True)
    label = Column(String)
    full_name = Column(String)
    short_name = Column(String)
