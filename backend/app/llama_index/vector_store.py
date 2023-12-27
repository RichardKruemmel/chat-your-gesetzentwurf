import os
from typing import List
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from llama_index import VectorStoreIndex
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import QdrantVectorStore
from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.indices.vector_store.retrievers import VectorIndexRetriever
from llama_index.response_synthesizers import get_response_synthesizer
from app.llama_index.llm import ada_2, llm_35, setup_service_context


def get_vector_store_credentials() -> str:
    try:
        load_dotenv()
        qdrant_api_key = os.environ["QDRANT_API_KEY"]
        qdrant_url = os.environ["QDRANT_API_URL"]
        return qdrant_api_key, qdrant_url
    except Exception as e:
        logging.error(f"An error occurred while reading the credentials: {e}")
        raise


def setup_vector_store(collection_name: str) -> QdrantVectorStore:
    try:
        qdrant_api_key, qdrant_url = get_vector_store_credentials()
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )
        try:
            qdrant_client.get_collection(collection_name)
        except Exception as e:
            logging.info(f"Creating collection: {collection_name}")
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=1536, distance="Cosine"),
            )
        vector_store = QdrantVectorStore(
            client=qdrant_client, collection_name=collection_name
        )
        logging.info("Vector store successfully set up.")
        return vector_store
    except Exception as e:
        logging.error(f"An error occurred while setting up the vector store: {e}")
        raise


def setup_index(collection_name) -> VectorStoreIndex:
    try:
        qdrant_api_key, qdrant_url = get_vector_store_credentials()
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )
        vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name=collection_name,
        )
        print("Vector store successfully set up.")
        service_context = setup_service_context("llm_35")
        print("Service context successfully set up.")
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, service_context=service_context
        )
        return index
    except Exception as e:
        logging.error(f"An error occurred while setting up the index: {e}")
        raise


def setup_query_engine(
    index: VectorStoreIndex, similarity_top_k: int = 10
) -> RetrieverQueryEngine:
    if index is None:
        raise ValueError("Index must be provided to set up the query engine.")

    try:
        service_context_llm = setup_service_context("llm_35")
        print("Service context successfully set up.")
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k,
            doc_ids=["69bfa330-8eb2-43fe-8b1a-5ac0a754b642"],
        )
        print("Retriever successfully set up.")
        response_synthesizer = get_response_synthesizer(
            response_mode="compact",
            service_context=service_context_llm,
            use_async=True,
            streaming=False,
        )
        print("Response synthesizer successfully set up.")
        return RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )
    except Exception as e:
        logging.error(f"An error occurred while setting up the query engine: {e}")
        raise


def main():
    # Test Case 1
    index = setup_index("election_programs")
    print("Index successfully set up.")
    query_engine = setup_query_engine(index)
    print("Query engine successfully set up.")
    result = query_engine.query(
        "Was sind die Kernthemen der SPD?",
    )
    print(f"Answer: {str(result)}")
    return result
