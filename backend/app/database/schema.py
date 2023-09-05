from pydantic import BaseModel
from typing import List
from datetime import datetime


# For the 'documents' table
class DocumentBase(BaseModel):
    name: str
    pdf_data: bytes


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int

    class Config:
        from_attributes = True


# For the 'embeddings' table
class EmbeddingBase(BaseModel):
    document_id: int
    text_embedding: str


class EmbeddingCreate(EmbeddingBase):
    pass


class Embedding(EmbeddingBase):
    id: int

    class Config:
        from_attributes = True


# For the 'users' table


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    files: list[str] = []
