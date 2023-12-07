import os
from dotenv import load_dotenv
from llama_index import PromptTemplate, SimpleDirectoryReader, VectorStoreIndex

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.metrics.critique import harmfulness
from ragas.llama_index import evaluate
from ragas.llms import LangchainLLM

from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings


from llama_index.node_parser import SentenceSplitter
from llama_index.evaluation import (
    DatasetGenerator,
    QueryResponseDataset,
)

from langfuse import Langfuse
from langfuse.model import (
    CreateTrace,
    CreateSpan,
    CreateGeneration,
    CreateEvent,
    CreateScore,
)


from app.llama_index.ingestion import setup_ingestion_pipeline
from app.llama_index.vector_store import setup_vector_store
from app.llama_index.llm import setup_service_context
from app.llama_index.templates import (
    TEXT_QUESTION_TEMPLATE,
    EVAL_QUESTION_GEN_TEMPLATE,
)
from app.utils.file import save_dataset_to_json
from app.utils.env import get_env_variable

EVAL_DATA_PATH = "app/eval/eval_data/eval_doc.pdf"
DATASET_JSON_PATH = "app/eval/eval_data/spd_2021_dataset.json"
EVAL_VECTOR_STORE_NAME = "election_programs_eval"
SERVICE_CONTEXT_VERSION = "3.5"
NUM_QUESTIONS_PER_CHUNK = 3
NUM_EVAL_NODES = 100

parser_dict = {
    "sent_parser_s2_o50": SentenceSplitter(chunk_size=256, chunk_overlap=50),
    "sent_parser_s2_o100": SentenceSplitter(chunk_size=256, chunk_overlap=100),
    "sent_parser_s5_o100": SentenceSplitter(chunk_size=512, chunk_overlap=100),
    "sent_parser_s5_o200": SentenceSplitter(chunk_size=512, chunk_overlap=200),
    "sent_parser_s10_o200": SentenceSplitter(chunk_size=1024, chunk_overlap=200),
    "sent_parser_s10_o500": SentenceSplitter(chunk_size=1024, chunk_overlap=500),
}


def generate_dataset():
    docs = SimpleDirectoryReader(input_files=[EVAL_DATA_PATH]).load_data()
    vector_store = setup_vector_store(EVAL_VECTOR_STORE_NAME)
    pipeline = setup_ingestion_pipeline(vector_store=vector_store)
    eval_nodes = pipeline.run(documents=docs)
    eval_service_context = setup_service_context(SERVICE_CONTEXT_VERSION)

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


def generate_ragas_qr_pairs(dataset_json_path):
    try:
        eval_dataset = QueryResponseDataset.from_json(dataset_json_path)
    except Exception as e:
        raise ValueError(f"Failed to load dataset from {dataset_json_path}: {e}")

    eval_questions, eval_answers = zip(*eval_dataset.qr_pairs)
    eval_answers = [[a] for a in eval_answers]
    return eval_questions, list(eval_answers)


def setup_ragas_llm():
    load_dotenv()
    try:
        api_base = get_env_variable("OPENAI_API_BASE")
        api_key = get_env_variable("OPENAI_API_KEY")
        api_version = get_env_variable("OPENAI_API_VERSION")
        deployment_name = get_env_variable("OPENAI_DEPLOYMENT_NAME")
    except EnvironmentError as e:
        raise e

    azure_model = AzureChatOpenAI(
        deployment_name=deployment_name,
        model=api_version,
        openai_api_key=api_key,
        openai_api_type="azure",
    )
    return LangchainLLM(azure_model)


def setup_ragas_embeddings():
    load_dotenv()
    try:
        api_base = get_env_variable("OPENAI_API_BASE")
        api_key = get_env_variable("OPENAI_API_KEY")
        api_version = get_env_variable("OPENAI_API_VERSION")
    except EnvironmentError as e:
        raise e

    azure_embeddings = AzureOpenAIEmbeddings(
        deployment="wahlwave-embedding",
        model="text-embedding-ada-002",
        openai_api_type="azure",
        openai_api_base=api_base,
        openai_api_key=api_key,
        openai_api_version=api_version,
    )
    return azure_embeddings


def run_ragas_evaluation():
    eval_questions, eval_answers = generate_ragas_qr_pairs(DATASET_JSON_PATH)
    eval_llm = setup_ragas_llm()
    eval_embeddings = setup_ragas_embeddings()
    eval_vector_store = setup_vector_store(EVAL_VECTOR_STORE_NAME)
    eval_service_context = setup_service_context(SERVICE_CONTEXT_VERSION)
    index = VectorStoreIndex.from_vector_store(
        vector_store=eval_vector_store, service_context=eval_service_context
    )
    query_engine = index.as_query_engine()
    metrics = [
        faithfulness,
    ]
    langfuse = setup_langfuse()
    faithfulness.llm = eval_llm
    faithfulness.embeddings = eval_embeddings
    harmfulness.llm = eval_llm
    harmfulness.embeddings = eval_embeddings
    answer_relevancy.llm = eval_llm
    context_precision.llm = eval_llm
    context_precision.embeddings = eval_embeddings
    context_recall.llm = eval_llm
    context_recall.embeddings = eval_embeddings

    query_engine.query = langfuse.trace(query_engine.retrieve())
    scores = {}
    for m in metrics:
        print(f"calculating {m.name}")
        scores[m.name] = m.score(query_engine, eval_questions, eval_answers)

    trace = langfuse.trace(CreateTrace(name="rag"))
    trace.span(
        CreateSpan(
            name="evaluation",
            input={"questions": eval_questions, "answers": eval_answers},
            output={"scores": scores},
        )
    )
    result = evaluate(query_engine, metrics, eval_questions, eval_answers)
    print(result)
    result.to_pandas()


def setup_langfuse():
    load_dotenv()
    try:
        secret_key = get_env_variable("LANGFUSE_SECRET_KEY")
        public_key = get_env_variable("LANGFUSE_PUBLIC_KEY")
    except EnvironmentError as e:
        raise e

    langfuse = Langfuse(public_key=public_key, secret_key=secret_key)
    return langfuse


def create_languse_dataset():
    fiqa_eval = generate_ragas_qr_pairs(DATASET_JSON_PATH)
    langfuse = setup_langfuse()
    for question, answer in fiqa_eval[:5]:
        trace = langfuse.trace(CreateTrace(name="rag"))

        trace.span(
            CreateSpan(
                name="generation",
                input={"question": question},
                output={"answer": answer},
            )
        )


if __name__ == "__main__":
    run_ragas_evaluation()
