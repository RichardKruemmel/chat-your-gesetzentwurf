from llama_index import VectorStoreIndex


def setup_query_engine(index: VectorStoreIndex, filters: dict = None):
    query_engine = index.as_chat_engine(filters=filters)
    return query_engine
