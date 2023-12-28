import logging
import os

from app.database.crud import insert_and_update
from app.database.database import Base, Session, engine
from app.database.models.party import Party
from app.database.models.parliament import Parliament
from app.database.models.election import Election
from app.database.models.election_program import ElectionProgram
from app.scraper.utils.api_utils import fetch_entity


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
            }
            elections.append(new_election_entry)
    sorted_elections = sorted(elections, key=lambda p: p["id"])
    insert_and_update(Election, sorted_elections)
    update_election_previous_election_id(api_elections)
    update_parliament_last_election_id()


def update_parliament_last_election_id() -> None:
    # TODO: THis needs refactoring or moving to crud.py
    api_parliaments = fetch_entity("parliaments")
    session = Session()
    try:
        for parliament_api_data in api_parliaments:
            if parliament_api_data["current_project"]:
                parliament_db_data = (
                    session.query(Parliament)
                    .filter(Parliament.id == parliament_api_data["id"])
                    .one_or_none()
                )
                if parliament_db_data and parliament_api_data["current_project"]:
                    parliament_db_data.last_election_id = parliament_api_data[
                        "current_project"
                    ]["id"]
        session.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
        session.rollback()
    finally:
        session.close()


def update_election_previous_election_id(api_elections) -> None:
    updated_elections = []
    for api_election in api_elections:
        if api_election["type"] == "election":
            previous_election_id = None
            if api_election["previous_period"]:
                previous_legislature_period_id = api_election["previous_period"]["id"]
                print(previous_legislature_period_id)
                previous_election = next(
                    (
                        election
                        for election in api_elections
                        if election["id"] == previous_legislature_period_id
                    ),
                    None,
                )
                print(previous_election)
                if previous_election["previous_period"]:
                    previous_election_id = previous_election["previous_period"]["id"]
                    print(previous_election_id)
            # TODO implement solution for the case that abgeordnetenwatch did not link to the previous election id
            new_election_entry = {
                "id": api_election["id"],
                "label": api_election["label"],
                "election_date": api_election["election_date"],
                "start_date_period": api_election["start_date_period"],
                "end_date_period": api_election["end_date_period"],
                "parliament_id": api_election["parliament"]["id"],
                "previous_election_id": previous_election_id,
            }
            updated_elections.append(new_election_entry)
    insert_and_update(Election, updated_elections)


def populate_election_programs() -> None:
    api_election_programs = fetch_entity("election-program")
    s3_bucket_url = os.getenv["S3_BUCKET_URL"]
    election_programs = [
        {
            "id": api_election_program["id"],
            "label": api_election_program["label"],
            "election_id": api_election_program["parliament_period"]["id"],
            "party_id": api_election_program["party"]["id"],
            "abgeordnetenwatch_file_url": api_election_program["file"],
            "file_cloud_url": f"{s3_bucket_url}/{api_election_program['parliament_period']['id']}/{api_election_program['id']}.pdf",
        }
        for api_election_program in api_election_programs
        if api_election_program["party"] is not None
        and api_election_program["file"] is not None
    ]
    insert_and_update(ElectionProgram, election_programs)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    populate_parties()
    populate_parliaments()
    populate_elections()
    populate_election_programs()
