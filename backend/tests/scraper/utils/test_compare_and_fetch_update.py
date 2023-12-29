import pytest
import logging
from unittest.mock import patch, mock_open
from app.scraper.utils.api_utils import fetch_missing_entity_items
from app.scraper.utils.compare_and_fetch_update import compare_and_fetch_update


@patch("app.scraper.utils.compare_and_fetch_update.fetch_missing_entity_items")
def test_compare_and_fetch_update_with_new_data(mock_fetch):
    entity = "parties"
    newest_api_id = 102
    last_db_id = 100
    mock_data = [
        {
            "id": 101,
            "entity_type": "party",
            "label": "Party A",
            "api_url": "https://www.abgeordnetenwatch.de/api/v2/parties/101",
            "full_name": "Party A",
            "short_name": "P A",
        },
        {
            "id": 102,
            "entity_type": "party",
            "label": "Party B",
            "api_url": "https://www.abgeordnetenwatch.de/api/v2/parties/102",
            "full_name": "Party B",
            "short_name": "P B",
        },
    ]

    # Set up the mock
    mock_fetch.return_value = mock_data

    # Call the function
    result = compare_and_fetch_update(entity, newest_api_id, last_db_id)

    # Assertions
    mock_fetch.assert_called_once_with(entity, last_db_id)
    assert result == mock_data


@patch("app.scraper.utils.compare_and_fetch_update.fetch_missing_entity_items")
def test_compare_and_fetch_update_with_no_new_data(mock_fetch):
    entity = "parties"
    newest_api_id = 100
    last_db_id = 102

    # Call the function
    result = compare_and_fetch_update(entity, newest_api_id, last_db_id)

    # Assertions
    mock_fetch.assert_not_called()
    assert result is None
