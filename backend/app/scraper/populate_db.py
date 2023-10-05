from backend.app.database.crud import insert_and_update
from backend.app.database.models.party import Party
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
