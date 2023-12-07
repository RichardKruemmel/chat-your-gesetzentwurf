from typing import Any, TypedDict, Dict, List
import logging
import requests
import time
import math

from app.scraper.utils.constants import BASE_URL, ENTITY_LIST, PAGE_SIZE


class ApiResponse(TypedDict):
    meta: Dict[str, Any]
    data: List[Any]


def validate_entity(entity: str):
    if entity not in ENTITY_LIST:
        raise Exception(f"{entity} is not a valid entity")


def get_total_entity_count(entity: str) -> int:
    url = f"{BASE_URL}/{entity}?range_end=0"
    result = fetch_json(url)
    return result["meta"]["result"]["total"]


def fetch_json(url: str) -> ApiResponse:
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logging.error(f"Request error: {err}")
        raise
    return response.json()


def fetch_entities_by_page(entity: str, page_nr: int) -> List[Any]:
    url = f"{BASE_URL}/{entity}?range_start={page_nr * PAGE_SIZE}&range_end={(page_nr + 1) * PAGE_SIZE - 1}"
    result: ApiResponse = fetch_json(url)
    return result["data"]


def fetch_all_pages(entity: str, page_count: int) -> List[Any]:
    entities = []
    for page_nr in range(page_count):
        page_entities = fetch_entities_by_page(entity, page_nr)
        logging.info(f"Page No.{page_nr} of {entity} is fetched")
        entities.extend(page_entities)
    return entities


def fetch_entity(entity: str) -> List[Any]:
    time_begin = time.time()
    validate_entity(entity)
    total_entity_count = get_total_entity_count(entity)
    page_count = math.ceil(total_entity_count / PAGE_SIZE)
    fetched_entities = fetch_all_pages(entity, page_count)
    logging.info(f"All data for {entity} is fetched.")
    time_end = time.time()
    logging.info(f"Total runtime of fetching {entity} is {time_end - time_begin}")
    return fetched_entities


def fetch_newest_entity_item(entity: str) -> List[Any]:
    validate_entity(entity)
    url = f"{BASE_URL}/{entity}?range_end=1"
    last_item = fetch_json(url)
    logging.info(f"Newest item for {entity} is fetched.")
    return last_item["data"]


def fetch_missing_entity_items(entity: str, last_id: int) -> List[Any]:
    validate_entity(entity)
    url = f"{BASE_URL}/{entity}?id[gt]={last_id}"
    missing_items = fetch_json(url)
    logging.info(f"Missing items for {entity} are fetched.")
    return missing_items["data"]
