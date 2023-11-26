import logging


from app.scraper.utils.constants import ENTITY_MODEL_MAPPING
from app.scraper.utils.api_utils import fetch_newest_entity_item
from app.database.database import Session
from app.database.models.election_programm import ElectionProgram
from app.scraper.utils.compare_and_fetch_update import compare_and_fetch_update
from app.database.crud import insert_and_update
from app.database.utils.db_utils import get_last_id_from_model


def update_db() -> None:
    for entity, model in ENTITY_MODEL_MAPPING.items():
        newest_entity_item = fetch_newest_entity_item(entity)
        if not newest_entity_item:
            logging.warning(f"No data returned from API for entity: {entity}")
            continue

        newest_api_id = newest_entity_item[0]["id"]
        last_db_id = get_last_id_from_model(model)

        new_data = compare_and_fetch_update(entity, newest_api_id, last_db_id)
        if new_data:
            insert_and_update(model, new_data)
            logging.info(f"Update in database for {entity} successful.")


def update_file_cloud_url(s3_bucket_url: str):
    db = Session()

    try:
        election_programs = db.query(ElectionProgram).all()

        for program in election_programs:
            new_url = f"{s3_bucket_url}/{program.election_id}/{program.id}.pdf"
            program.file_cloud_url = new_url

        db.commit()
        logging.info("All file_cloud_urls have been updated successfully.")

    except Exception as e:
        db.rollback()
        logging.error(f"An error occurred while updating file_cloud_urls: {e}")

    finally:
        db.close()
