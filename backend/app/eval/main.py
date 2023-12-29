from app.eval.constants import VERSION
from app.eval.dataset_generation import generate_dataset
from app.eval.langfuse_integration import create_langfuse_traces
from app.eval.ragas_eval import run_ragas_evaluation


def main():
    generate_dataset()
    eval = run_ragas_evaluation()
    create_langfuse_traces(eval, version=VERSION)
