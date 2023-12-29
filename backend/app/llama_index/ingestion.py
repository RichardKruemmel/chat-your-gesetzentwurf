from typing import List
from llama_index import Document
from llama_index.ingestion import IngestionPipeline, IngestionCache
from llama_index.ingestion.cache import RedisCache
from llama_index.text_splitter import SentenceSplitter
from llama_index.extractors import (
    QuestionsAnsweredExtractor,
    SummaryExtractor,
    KeywordExtractor,
)
from llama_index.vector_stores import QdrantVectorStore
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
import logging
import os
from dotenv import load_dotenv
import requests

from app.llama_index.vector_store import setup_vector_store
from app.llama_index.llm import llm_35
from app.llama_index.templates import (
    SUMMARY_EXTRACT_TEMPLATE,
    QUESTION_GEN_TEMPLATE,
)
from app.database.database import Session
from app.database.models.election_program import ElectionProgram
from app.scraper.utils.pdf_downloader import download_pdf
from app.llama_index.loader import load_docs


def setup_ingestion_pipeline(vector_store: QdrantVectorStore):
    load_dotenv()
    api_base = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")
    api_version = os.getenv("OPENAI_API_VERSION")
    transformations = [
        SentenceSplitter(chunk_size=512),
        AzureOpenAIEmbedding(
            azure_deployment="wahlwave-embedding",
            api_key=api_key,
            azure_endpoint=api_base,
            api_version=api_version,
            model="text-embedding-ada-002",
            embed_batch_size=16,
        ),
        QuestionsAnsweredExtractor(llm_35, prompt_template=QUESTION_GEN_TEMPLATE),
        SummaryExtractor(llm_35, prompt_template=SUMMARY_EXTRACT_TEMPLATE),
        KeywordExtractor(llm_35, num_keywords=3),
    ]

    try:
        pipeline = IngestionPipeline(
            transformations=transformations,
            vector_store=vector_store,
            cache=IngestionCache(
                cache=RedisCache(), collection="election_program_cache"
            ),
        )
        logging.info("Ingestion pipeline successfully set up.")
        return pipeline
    except Exception as e:
        logging.error(f"An error occurred while setting up the ingestion pipeline: {e}")
        raise


def ingest_data(vector_store: QdrantVectorStore, documents: List[Document]):
    ingestion_pipeline = setup_ingestion_pipeline(vector_store=vector_store)
    try:
        if len(documents) == 0:
            raise ValueError("No document provided for ingestion.")
        index = ingestion_pipeline.run(documents=documents)
        logging.info(f"Document successfully ingested.")
        return index.index
    except Exception as e:
        logging.error(f"An error occurred while ingesting Document: {e}")
        raise


def query_and_ingest_election_programs(election_id: int, party_id: int):
    db = Session()
    try:
        # Query for election programs with election_id  and main parties (party_id < 10)
        election_programs = (
            db.query(ElectionProgram)
            .filter(
                ElectionProgram.election_id == election_id,
                ElectionProgram.party_id == party_id,
            )
            .all()
        )
        vector_store = setup_vector_store("election_programs")
        for program in election_programs:
            if program.vectorized == True:
                logging.info(
                    f"Election program with id={program.id} is already vectorized."
                )
                continue
            # Define the path where the PDF will be saved
            save_path = os.path.join(
                "./../docs", f"{program.election_id}_{program.id}.pdf"
            )
            logging.info(f"Downloading PDF for election_program_id={program.id}")

            # Download the PDF
            download_pdf(program.file_cloud_url, save_path)
            logging.info(f"Downloaded PDF to {save_path}")

            documents = load_docs(save_path, program)

            # Run the ingestion pipeline for the downloaded PDF
            ingest_data(vector_store=vector_store, documents=documents)
            logging.info(f"Successfully ingested PDF into index")

            # Delete the PDF
            os.remove(save_path)
            logging.info(f"Deleted PDF from {save_path}")
            # set vectorized to True
            program.vectorized = True
            db.commit()
            logging.info(
                f"Successfully set vectorized to True for election_program_id={program.id}"
            )

    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        logging.error(f"An error occurred during the query and ingestion process: {e}")
    finally:
        db.close()


def delete_document(document_id: str):
    try:
        vector_store = setup_vector_store("election_programs")
        vector_store.delete(document_id)
        logging.info("All documents successfully deleted.")
    except Exception as e:
        logging.error(f"An error occurred while deleting documents: {e}")
        raise
