from backend.app.database.crud import insert_and_update
from backend.app.database.models.party import Party
from backend.app.database.models.parliament import Parliament
from backend.app.database.models.election import Election
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
            "label_external_long": api_parliament["label_external_long"],
            "current_election": api_parliament["current_project"],
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
