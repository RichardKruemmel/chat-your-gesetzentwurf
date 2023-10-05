from sqlalchemy.orm import Session
from logging import logging

from backend.app.database.crud import insert_and_update
from backend.app.database.database import Base, engine
from backend.app.database.models.party import Party
from backend.app.database.models.parliament import Parliament
from backend.app.database.models.election import Election
from backend.app.database.models.election_programm import ElectionProgram
from backend.app.scraper.utils import fetch_entity


def populate_parties() -> None:
    api_parties = fetch_entity("parties")
    parties = [
        {
            "id": api_party["id"],
            "label": api_party["label"],
            "full_name": api_party["full_name"],
            "short_name": api_party["short_name"],
        }
        for api_party in api_parties
    ]
    insert_and_update(Party, parties)


def populate_parliaments() -> None:
    api_parliaments = fetch_entity("parliaments")
    parliaments = [
        {
            "id": api_parliament["id"],
            "label": api_parliament["label"],
            "abgeordnetenwatch_url": api_parliament["abgeordnetenwatch_url"],
            "label_long": api_parliament["label_external_long"],
        }
        for api_parliament in api_parliaments
    ]
    insert_and_update(Parliament, parliaments)


def populate_elections() -> None:
    api_elections = fetch_entity("parliament-periods")
    elections = []
    for api_election in api_elections:
        if api_election["type"] == "election":
            new_election_entry = {
                "id": api_election["id"],
                "label": api_election["label"],
                "election_date": api_election["election_date"],
                "start_date_period": api_election["start_date_period"],
                "end_date_period": api_election["end_date_period"],
                "parliament_id": api_election["parliament"]["id"],
                "previous_election": api_election["previous_period"]["id"]
                if api_election["previous_period"]
                else None,
            }
            elections.append(new_election_entry)
    sorted_elections = sorted(elections, key=lambda p: p["id"])
    insert_and_update(Election, sorted_elections)
    update_parliament_last_election_id()


def update_parliament_last_election_id() -> None:
    # TODO: THis needs refactoring or moving to crud.py
    api_parliaments = fetch_entity("parliaments")
    session = Session()
    try:
        for parliament_data in api_parliaments:
            if parliament_data["last_election_id"]:
                parliament = (
                    session.query(Parliament)
                    .filter(Parliament.id == parliament_data["id"])
                    .one_or_none()
                )
                if parliament and parliament_data["current_project"]:
                    parliament.last_election_id = parliament_data["current_project"][
                        "id"
                    ]
        session.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
        session.rollback()
    finally:
        session.close()


def populate_election_programs() -> None:
    api_election_programs = fetch_entity("election-program")
    election_programs = [
        {
            "id": api_election_program["id"],
            "label": api_election_program["label"],
            "election_id": api_election_program["parliament_period"]["id"],
            "party_id": api_election_program["party"]["id"],
            "abgeordnetenwatch_file_url": api_election_program["file"],
        }
        for api_election_program in api_election_programs
    ]
    insert_and_update(ElectionProgram, election_programs)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    populate_parties()
    populate_parliaments()
    populate_elections()
    populate_election_programs()
