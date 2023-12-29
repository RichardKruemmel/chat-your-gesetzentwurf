from celery import Celery
from app.scraper.scripts.update_db import update_db
import time
import logging

from app.database.database import Session


celery = Celery(__name__, broker="redis://redis:6379/0", backend="redis://redis:6379/0")


@celery.task
def update_db_task():
    update_db(Session)
    return True


@celery.task
def divide(x, y):
    time.sleep(5)
    result = x / y
    logging.info(f"Result: {result}")
    return result
