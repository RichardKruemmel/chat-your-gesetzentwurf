import json


def save_dataset_to_json(dataset, path: str) -> None:
    """Save json."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataset.dict(), f, ensure_ascii=False, indent=4)
