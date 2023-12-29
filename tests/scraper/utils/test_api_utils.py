import logging
import requests
import pytest
from unittest.mock import patch
import time

from app.scraper.utils.api_utils import (
    fetch_entities_by_page,
    fetch_entity,
    fetch_json,
    fetch_missing_entity_items,
    get_total_entity_count,
    validate_entity,
)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise requests.exceptions.HTTPError(f"HTTP Error: {self.status_code}")


# Test validate_entity


def test_validate_entity_valid():
    valid_entity = "parties"
    try:
        validate_entity(valid_entity)
        assert True
    except Exception:
        assert (
            False
        ), f"validate_entity raised an exception for a valid entity: {valid_entity}"


def test_validate_entity_invalid():
    invalid_entity = "invalid_entity"
    with pytest.raises(Exception) as excinfo:
        validate_entity(invalid_entity)
    assert str(excinfo.value) == f"{invalid_entity} is not a valid entity"


def test_validate_entity_empty():
    empty_entity = ""
    with pytest.raises(Exception) as excinfo:
        validate_entity(empty_entity)
    assert str(excinfo.value) == f"{empty_entity} is not a valid entity"


def test_validate_entity_whitespace():
    whitespace_entity = "   "
    with pytest.raises(Exception) as excinfo:
        validate_entity(whitespace_entity)
    assert str(excinfo.value) == f"{whitespace_entity} is not a valid entity"


# Test get_total_entity_count


def test_get_total_entity_count_valid(mocker):
    entity = "parties"
    expected_count = 10
    mocker.patch(
        "app.scraper.utils.api_utils.fetch_json",
        return_value={"meta": {"result": {"total": expected_count}}},
    )
    result = get_total_entity_count(entity)
    assert result == expected_count


def test_get_total_entity_count_invalid(mocker):
    entity = "invalid_entity"
    mocker.patch(
        "app.scraper.utils.api_utils.fetch_json",
        side_effect=Exception("Invalid entity"),
    )
    with pytest.raises(Exception):
        get_total_entity_count(entity)


# Test fetch_json


def test_fetch_json_success(mocker):
    url = "https://example.com/api"
    expected_response = {"data": "example"}
    mocker.patch("requests.get", return_value=MockResponse(expected_response, 200))
    result = fetch_json(url)
    assert result == expected_response


def test_fetch_json_failure(mocker):
    url = "https://example.com/api"
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Request error"),
    )
    with pytest.raises(requests.exceptions.RequestException):
        fetch_json(url)


# Test fetch_entities_by_page


def test_fetch_entities_by_page_success(mocker):
    entity = "parties"
    page_nr = 1
    expected_response = {"data": ["entity1", "entity2"]}
    mocker.patch(
        "app.scraper.utils.api_utils.fetch_json", return_value=expected_response
    )
    result = fetch_entities_by_page(entity, page_nr)
    assert result == expected_response["data"]


def test_fetch_entities_by_page_failure(mocker):
    entity = "invalid_entity"
    page_nr = 1
    mocker.patch(
        "app.scraper.utils.api_utils.fetch_json",
        side_effect=Exception("Invalid entity"),
    )
    with pytest.raises(Exception):
        fetch_entities_by_page(entity, page_nr)


# Test fetch_entity


def test_fetch_entity(mocker):
    entity = "example_entity"
    total_entity_count = 100
    mocker.patch("app.scraper.utils.api_utils.validate_entity")
    mocker.patch(
        "app.scraper.utils.api_utils.get_total_entity_count",
        return_value=total_entity_count,
    )
    mocker.patch(
        "app.scraper.utils.api_utils.fetch_all_pages",
        return_value=[f"item_{i}" for i in range(total_entity_count)],
    )
    mocker.patch("time.time", side_effect=[0, 1])
    mocker.patch("logging.info")
    result = fetch_entity(entity)
    assert result == [f"item_{i}" for i in range(total_entity_count)]
    assert time.time.call_count == 2
    logging.info.assert_any_call(f"All data for {entity} is fetched.")
    logging.info.assert_any_call(f"Total runtime of fetching {entity} is 1")


# Test fetch_missing_entity_items


def test_fetch_missing_entity_items(mocker):
    entity = "parties"
    last_id = 100
    expected_response = {"data": ["item1", "item2"]}
    mocker.patch("app.scraper.utils.api_utils.validate_entity")
    mocker.patch(
        "app.scraper.utils.api_utils.fetch_json", return_value=expected_response
    )
    mocker.patch("logging.info")
    result = fetch_missing_entity_items(entity, last_id)
    assert result == expected_response["data"]
