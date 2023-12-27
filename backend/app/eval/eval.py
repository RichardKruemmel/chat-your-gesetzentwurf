import logging
from dotenv import load_dotenv
from llama_index import VectorStoreIndex
import pandas as pd

from ragas.metrics import answer_relevancy
from ragas.llama_index import evaluate
from ragas.llms import LangchainLLM

from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import AzureOpenAIEmbeddings


from langfuse import Langfuse
from langfuse.model import (
    CreateTrace,
    CreateSpan,
    CreateScore,
)


from app.llama_index.vector_store import setup_vector_store
from app.llama_index.llm import setup_service_context

from app.utils.env import get_env_variable


def setup_ragas_llm():
    load_dotenv()
    try:
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
        deployment = get_env_variable("OPENAI_DEPLOYMENT_EMBEDDINGS")
        api_base = get_env_variable("OPENAI_API_BASE")
        api_key = get_env_variable("OPENAI_API_KEY")
        api_version = get_env_variable("OPENAI_API_VERSION")
    except EnvironmentError as e:
        raise e

    azure_embeddings = AzureOpenAIEmbeddings(
        azure_deployment=deployment,
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
    eval_service_context = setup_service_context(SERVICE_CONTEXT_VERSION, azure=True)
    index = VectorStoreIndex.from_vector_store(
        vector_store=eval_vector_store, service_context=eval_service_context
    )
    query_engine = index.as_query_engine()
    metrics = EVAL_METRICS

    answer_relevancy.embeddings = eval_embeddings
    for m in metrics:
        m.__setattr__("llm", eval_llm)
        m.__setattr__("embeddings", eval_embeddings)

    result = evaluate(query_engine, metrics, eval_questions, eval_answers)
    df = result.to_pandas()
    df.to_csv("app/eval/eval_data/ragas_eval.csv", index=False)
    eval = pd.read_csv("app/eval/eval_data/ragas_eval.csv", sep=",")
    return eval


def setup_langfuse():
    load_dotenv()
    try:
        secret_key = get_env_variable("LANGFUSE_SECRET_KEY")
        public_key = get_env_variable("LANGFUSE_PUBLIC_KEY")
    except EnvironmentError as e:
        raise e
    langfuse = Langfuse(public_key=public_key, secret_key=secret_key)
    logging.info("Langfuse successfully set up.")
    return langfuse


def create_langfuse_traces(fiqa_eval=None, version="0.1.0"):
    if fiqa_eval is None:
        # Load csv file
        fiqa_eval = pd.read_csv("app/eval/eval_data/ragas_eval.csv", sep=",")
    langfuse = setup_langfuse()
    for index, row in fiqa_eval.iterrows():
        trace = langfuse.trace(CreateTrace(name="wahlwave", version=version))
        trace.span(
            CreateSpan(
                name="retrieval",
                input={"question": row["question"]},
                output={"contexts": row["contexts"]},
            )
        )
        trace.span(
            CreateSpan(
                name="generation",
                input={"question": row["question"]},
                output={"answer": row["answer"]},
            )
        )
        for metric in EVAL_METRICS:
            trace.score(CreateScore(name=metric.name, value=row[metric.name]))

    langfuse.flush()


def get_traces(name=None, limit=None, user_id=None):
    all_data = []
    page = 1
    langfuse = setup_langfuse()
    while True:
        response = langfuse.client.trace.list(name=name, page=page, user_id=user_id)
        if not response.data:
            break
        page += 1
        all_data.extend(response.data)
        if len(all_data) > limit:
            break
    print(all_data[:limit])
    return all_data[:limit]


def generate_evals():
    generate_dataset()
    eval = run_ragas_evaluation()
    create_langfuse_traces(eval, version=VERSION)
