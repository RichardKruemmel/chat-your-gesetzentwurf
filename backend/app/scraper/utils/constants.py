from app.database import models


ENTITY_LIST = ["parties", "election-program", "parliaments", "parliament-periods"]
PAGE_SIZE = 1000
BASE_URL = "https://www.abgeordnetenwatch.de/api/v2"
ENTITY_MODEL_MAPPING = {
    "parties": models.Party,
    "election-program": models.ElectionProgram,
    "parliaments": models.Parliament,
    "parliament-periods": models.Election,
}
