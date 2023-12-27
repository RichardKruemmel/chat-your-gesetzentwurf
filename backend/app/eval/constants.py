from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall

EVAL_DATA_PATH = "app/eval/eval_data/eval_doc.pdf"
DATASET_JSON_PATH = "app/eval/eval_data/spd_2021_dataset.json"
EVAL_VECTOR_STORE_NAME = "election_programs_eval"
SERVICE_CONTEXT_VERSION = "3.5"
NUM_QUESTIONS_PER_CHUNK = 3
NUM_EVAL_NODES = 100
EVAL_METRICS = [
    Faithfulness(),
    ContextPrecision(),
    ContextRecall(),
    AnswerRelevancy(),
]
VERSION = "0.1.1"
