from sqlalchemy import Column, Integer, String, Date, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Embedding(Base):
    __tablename__ = "embedding"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    text_embedding = Column(Text)

    document = relationship("Document", back_populates="embedding")
