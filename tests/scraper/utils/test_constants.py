from app.database import models
from app.scraper.utils.constants import ENTITY_MODEL_MAPPING


def test_entity_model_mapping():
    for entity, model in ENTITY_MODEL_MAPPING.items():
        assert hasattr(
            models, model.__name__
        ), f"Model {model.__name__} does not exist for entity {entity}"
