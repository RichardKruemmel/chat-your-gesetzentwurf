import logging
from llama_index import SimpleDirectoryReader

from app.database.models.election_programm import ElectionProgram


def load_docs(save_path: str, program: ElectionProgram):
    documents = SimpleDirectoryReader(input_files=[save_path]).load_data()
    logging.info(f"Loaded PDF into Document object")

    for doc in documents:
        metadata = doc.metadata
        extra_info = get_metadata(
            program_id=program.id,
            party_id=program.party_id,
            election_id=program.election_id,
        )
        metadata.update(extra_info)
        doc.metadata = metadata
    return documents


def get_metadata(program_id: int, party_id: int, election_id: int):
    return {
        "election_id": election_id,
        "party_id": party_id,
        "election_program_id": program_id,
        "group_id": program_id,
    }
