from backend.app.database.crud import insert_and_update
from backend.app.database.models.party import Party
from backend.app.database.models.parliament import Parliament
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
