from dotenv import load_dotenv
import pandas as pd
import logging
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langfuse.model import (
    CreateTrace,
    CreateSpan,
    CreateScore,
)

from app.eval.constants import EVAL_METRICS
from app.utils.env import get_env_variable


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

    logging.info("Langfuse traces successfully created.")
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
    logging.info("Langfuse traces successfully retrieved.")
    return all_data[:limit]


def get_langfuse_callback_manager():
    secret_key = get_env_variable("LANGFUSE_SECRET_KEY")
    public_key = get_env_variable("LANGFUSE_PUBLIC_KEY")
    return CallbackHandler(public_key, secret_key)
