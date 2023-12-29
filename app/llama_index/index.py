from llama_index import VectorStoreIndex
from app.llama_index.vector_store import setup_vector_store
from app.llama_index.llm import setup_service_context


def setup_index():
    vector_store = setup_vector_store("election_programs")
    service_context = setup_service_context("3.5")
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        service_context=service_context,
    )
    return index
