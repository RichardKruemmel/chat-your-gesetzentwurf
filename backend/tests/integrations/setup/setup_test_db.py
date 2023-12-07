from datetime import date
from sqlalchemy import create_engine

from app.database.database import Base, Session
from app.database import models


def setup_test_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)

    session = Session()
    parties = [
        models.Party(id=1, label="Party A", full_name="Party A", short_name="P A"),
        models.Party(id=2, label="Party B", full_name="Party B", short_name="P B"),
    ]

    parliament = models.Parliament(
        id=1,
        label="Parliament 1",
        abgeordnetenwatch_url="https://example.com/parliament1",
        label_long="The First Parliament",
        last_election_id=1,
    )

    elections = [
        models.Election(
            id=1,
            label="Election 1",
            election_date=date(2021, 1, 1),
            start_date_period=date(2021, 1, 1),
            end_date_period=date(2021, 12, 31),
            parliament_id=1,
            previous_election_id=0,
        ),
    ]

    election_programs = [
        models.ElectionProgram(
            id=1,
            label="Election Program 1",
            election_id=1,
            party_id=1,
            abgeordnetenwatch_file_url="http://localhost:8000/api/program/1",
            file_cloud_url="https://s3.example.com/program1.pdf",
            vector_store_id=101,
        ),
        models.ElectionProgram(
            id=2,
            label="Election Program 2",
            election_id=1,
            party_id=2,
            abgeordnetenwatch_file_url="http://localhost:8000/api/program/2",
            file_cloud_url="https://s3.example.com/program2.pdf",
            vector_store_id=102,
        ),
    ]
    session.add_all(parties)
    session.add(parliament)
    session.add_all(elections)
    session.add_all(election_programs)

    session.commit()
    return engine, session
