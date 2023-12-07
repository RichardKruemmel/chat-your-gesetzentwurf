from llama_index import (
    VectorStoreIndex,
    SummaryIndex,
    ServiceContext,
)
from llama_index.node_parser import SentenceSplitter
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import OpenAIAgent

from app.llama_index.llm import llm_35, llm_40, messages
from app.llama_index.index import load_docs


programs = {
    "SPD": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/SPD_Wahlprogramm_BTW2021.pdf",
    "FDP": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/FDP_Wahlprogramm_BTW2021.pdf",
    "AFD": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/AfD_Wahlprogramm_BTW2021.pdf",
    "CDU": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/CDU-CSU_Wahlprogramm_BTW2021.pdf",
    "Grüne": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/B90DieGr%C3%BCnen_Wahlprogramm_BTW2021.pdf",
}

program_documents = {}
documents = []

for party, url in programs.items():
    document = load_docs(url)
    program_documents[party] = document


service_context = ServiceContext.from_defaults(llm=llm_35)

node_parser = SentenceSplitter()

agents = {}
query_engines = {}
all_nodes = []

for party, text_content in program_documents.items():
    nodes = node_parser.get_nodes_from_text(text_content)
    all_nodes.extend(nodes)

    # build vector index
    vector_index = VectorStoreIndex(
        nodes,
        service_context=service_context,
        index_name=f"{party}_election_programs",
        vector_store_name=f"{party}_election_programs",
    )

    # build summary index (you need to implement or adjust this part based on your summary method)
    summary_index = SummaryIndex(nodes, service_context=service_context)

    # define query engines
    vector_query_engine = vector_index.as_query_engine()
    summary_query_engine = summary_index.as_query_engine()

    # define tools
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="vector_tool",
                description=(
                    f"Useful for questions related to specific aspects of the {party}'s election program."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=summary_query_engine,
            metadata=ToolMetadata(
                name="summary_tool",
                description=(
                    f"Useful for requests that require a holistic summary of the {party}'s election program."
                ),
            ),
        ),
    ]

    function_llm = llm_35
    agent = OpenAIAgent.from_tools(
        query_engine_tools,
        llm=function_llm,
        verbose=True,
        system_prompt=f"You are a specialized agent designed to answer queries about the {party}'s election program.",
    )

    agents[party] = agent
    query_engines[party] = vector_query_engine
