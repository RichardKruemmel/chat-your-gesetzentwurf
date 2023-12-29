from typing import List, TypeVar, Type
from sqlalchemy import select
from app.database.database import Base
from app.database.database import Session
import logging

T = TypeVar("T", bound=Base)


def get_session():
    with Session() as session:
        try:
            yield session
        finally:
            session.close()


def load_entity_from_db(model: Type[T]) -> List[T]:
    try:
        with Session() as session:
            entity = session.scalars(select(model).order_by(model.id)).all()
        return entity
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        raise


def get_last_id_from_model(model: Type[T]) -> int:
    try:
        with Session() as session:
            last_id = (
                session.scalars(select(model).order_by(model.id.desc())).first().id
            )
            return last_id
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        raise
