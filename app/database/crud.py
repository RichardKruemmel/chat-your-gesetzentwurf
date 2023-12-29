import logging
from typing import Optional, Type, List, Dict

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import insert as generic_insert

from app.database.models import ElectionProgram, Party, Election
from .database import Base, Session
from app.database.schema import User


def get_user(db: Session, username: str):
    return db.query(User).filter(User.email == username).first()


def insert_and_update(
    model: Type[Base], data: List[Dict], session: Optional[Session]
) -> None:
    if not session:
        session = Session()
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


def get_vectorized_election_programs_from_db(db: Session):
    return (
        db.query(
            ElectionProgram.id,
            ElectionProgram.party_id,
            ElectionProgram.election_id,
            Party.full_name,
            Election.label,
        )
        .join(Party, ElectionProgram.party_id == Party.id)
        .join(Election, ElectionProgram.election_id == Election.id)
        .filter(ElectionProgram.vectorized == True)
        .all()
    )
