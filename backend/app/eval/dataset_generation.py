import logging
from llama_index import SimpleDirectoryReader, PromptTemplate
from llama_index.evaluation import DatasetGenerator, QueryResponseDataset
from app.eval.constants import (
    DATASET_JSON_PATH,
    EVAL_DATA_PATH,
    EVAL_VECTOR_STORE_NAME,
    NUM_EVAL_NODES,
    NUM_QUESTIONS_PER_CHUNK,
    SERVICE_CONTEXT_VERSION,
)
from app.llama_index.templates import EVAL_QUESTION_GEN_TEMPLATE, TEXT_QUESTION_TEMPLATE
from app.llama_index.ingestion import setup_ingestion_pipeline
from app.llama_index.vector_store import setup_vector_store
from app.llama_index.llm import setup_service_context
from app.utils.file import save_dataset_to_json


def generate_dataset():
    docs = SimpleDirectoryReader(input_files=[EVAL_DATA_PATH]).load_data()
    vector_store = setup_vector_store(EVAL_VECTOR_STORE_NAME)
    pipeline = setup_ingestion_pipeline(vector_store=vector_store)
    eval_nodes = pipeline.run(documents=docs)
    eval_service_context = setup_service_context(SERVICE_CONTEXT_VERSION)
    logging.info(f"Generated {len(eval_nodes)} nodes.")

    dataset_generator = DatasetGenerator(
        eval_nodes[:NUM_EVAL_NODES],
        service_context=eval_service_context,
        show_progress=True,
        num_questions_per_chunk=NUM_QUESTIONS_PER_CHUNK,
        text_question_template=PromptTemplate(TEXT_QUESTION_TEMPLATE),
        question_gen_query=EVAL_QUESTION_GEN_TEMPLATE,
    )
    eval_dataset = dataset_generator.generate_dataset_from_nodes(num=NUM_EVAL_NODES)
    save_dataset_to_json(eval_dataset, DATASET_JSON_PATH)
    logging.info(f"Saved dataset to {DATASET_JSON_PATH}.")


def generate_ragas_qr_pairs(dataset_json_path):
    try:
        eval_dataset = QueryResponseDataset.from_json(dataset_json_path)
    except Exception as e:
        raise ValueError(f"Failed to load dataset from {dataset_json_path}: {e}")

    eval_questions, eval_answers = zip(*eval_dataset.qr_pairs)
    eval_answers = [[a] for a in eval_answers]
    logging.info(f"Generated {len(eval_questions)} question-response pairs.")
    return eval_questions, list(eval_answers)
