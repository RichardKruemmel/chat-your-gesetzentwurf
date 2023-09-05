from sqlalchemy.orm import Session
from app.database.schema import User


def get_user(db: Session, username: str):
    return db.query(User).filter(User.email == username).first()
