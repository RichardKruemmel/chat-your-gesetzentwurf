from sqlalchemy import Column, Integer, String, Date, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Date)
    pdf_data = Column(LargeBinary)

    embeddings = relationship("Embedding", back_populates="document")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    text_embedding = Column(Text)

    document = relationship("Document", back_populates="embeddings")
