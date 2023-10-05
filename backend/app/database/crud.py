from typing import Any, List

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from .database import Session
from app.database.schema import User


def get_user(db: Session, username: str):
    return db.query(User).filter(User.email == username).first()


def insert_and_update(model: Any, data: List[Any]) -> None:
    session = Session()
    stmt = insert(model).values(data)
    stmt = stmt.on_conflict_do_update(
        constraint=f"{model.__tablename__}_pkey",
        set_={col.name: col for col in stmt.excluded if not col.primary_key},
    )
    session.execute(stmt)
    session.commit()
    session.close()
