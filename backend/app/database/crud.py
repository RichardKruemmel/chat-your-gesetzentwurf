import logging
from typing import Optional, Type, List, Dict

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import insert as generic_insert


from .database import Base, Session as DatabaseSession
from app.database.schema import User


def get_user(db: Session, username: str):
    return db.query(User).filter(User.email == username).first()


def insert_and_update(
    model: Type[Base], data: List[Dict], session: Optional[Session]
) -> None:
    if not session:
        session = DatabaseSession()
    try:
        if session.bind.dialect.name == "postgresql":
            # PostgreSQL-specific INSERT ... ON CONFLICT
            stmt = pg_insert(model).values(data)
            stmt = stmt.on_conflict_do_update(
                constraint=f"{model.__tablename__}_pkey",
                set_={col.name: col for col in stmt.excluded if not col.primary_key},
            )
        else:
            # Generic SQL for other databases like SQLite
            stmt = generic_insert(model).values(data)

        session.execute(stmt)
        session.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
        session.rollback()
    finally:
        session.close()
