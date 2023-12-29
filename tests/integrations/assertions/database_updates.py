import os
import json

from app.scraper.utils.constants import ENTITY_MODEL_MAPPING


def assert_correct_database_updates(session):
    test_data_directory = "tests/integrations/test_data"

    for entity, model in ENTITY_MODEL_MAPPING.items():
        newest_file_path = os.path.join(test_data_directory, f"{entity}_newest.json")
        updates_file_path = os.path.join(test_data_directory, f"{entity}_updates.json")

        if not os.path.exists(newest_file_path) or not os.path.exists(
            updates_file_path
        ):
            continue

        # Load the expected newest and updated data for this entity from JSON files
        with open(newest_file_path, "r") as f:
            newest_data = json.load(f)["data"][0]

        with open(updates_file_path, "r") as f:
            updates_data = json.load(f)["data"]

        # Assert that the newest item exists in the database
        newest_item_in_db = session.get(model, newest_data["id"])
        assert (
            newest_item_in_db is not None
        ), f"Newest item for {entity} not found in DB"

        # Assert the fields of the newest item match
        for key, value in newest_data.items():
            assert (
                getattr(newest_item_in_db, key) == value
            ), f"Mismatch in {entity} for field {key}"

        # For each update, check that the item exists and matches the test data
        for update in updates_data:
            updated_item_in_db = session.get(model, update["id"])
            assert (
                updated_item_in_db is not None
            ), f"Updated item {update['id']} for {entity} not found in DB"

            # Assert the fields of the updated item match
            for key, value in update.items():
                assert (
                    getattr(updated_item_in_db, key) == value
                ), f"Mismatch in {entity} update for field {key}"

    print("Database updates validated successfully.")
