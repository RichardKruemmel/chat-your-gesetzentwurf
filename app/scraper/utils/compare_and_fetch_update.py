import logging
from typing import List, Any, Optional

from app.scraper.utils.api_utils import fetch_missing_entity_items


def compare_and_fetch_update(
    entity: str, newest_api_id: int, last_db_id: int
) -> Optional[List[Any]]:
    if newest_api_id > last_db_id:
        logging.info(f"New data detected for {entity}. Updating database table.")
        return fetch_missing_entity_items(entity, last_db_id)
    else:
        logging.info(f"No new data for {entity}. No update necessary.")
        return None
