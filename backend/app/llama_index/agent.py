import logging
import nest_asyncio
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import OpenAIAgent
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters

from app.llama_index.llm import llm_35, setup_service_context
from app.llama_index.index import setup_index
from app.llama_index.query_engine import setup_query_engine
from app.database.crud import get_vectorized_election_programs_from_db
from app.database.database import Session


programs = {
    "SPD": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/SPD_Wahlprogramm_BTW2021.pdf",
    "FDP": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/FDP_Wahlprogramm_BTW2021.pdf",
    "AFD": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/AfD_Wahlprogramm_BTW2021.pdf",
    "CDU": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/CDU-CSU_Wahlprogramm_BTW2021.pdf",
    "Grüne": "https://www.abgeordnetenwatch.de/sites/default/files/election-program-files/B90DieGr%C3%BCnen_Wahlprogramm_BTW2021.pdf",
}


def setup_llama_agent():
    session = Session()
    vectorized_election_programs = get_vectorized_election_programs_from_db(session)
    logging.info(f"Loaded {len(vectorized_election_programs)} vectorized programs.")
    # get party name
    vector_tools = []
    agents = {}
    query_engines = {}
    for program in vectorized_election_programs:
        meta_data_filters = MetadataFilters(
            filters=[
                ExactMatchFilter(key="group_id", value=program.id),
                ExactMatchFilter(key="election_id", value=program.election_id),
                ExactMatchFilter(key="party_id", value=program.party_id),
            ]
        )

        # define query engines
        vector_index = setup_index()
        vector_query_engine = setup_query_engine(
            vector_index, filters=meta_data_filters
        )
        # define tools
        query_engine_tools = [
            QueryEngineTool(
                query_engine=vector_query_engine,
                metadata=ToolMetadata(
                    name=f"vector_tool_{program.full_name}",
                    description=(
                        f"Nützlich für Fragen zu spezifischen Aspekten des Wahlprogramms der {program.full_name} für die {program.label}."
                    ),
                ),
            )
        ]

        logging.info(f"Loaded query engine tool for {program.full_name}.")

        # build agent
        function_llm = llm_35
        agent = OpenAIAgent.from_tools(
            query_engine_tools,
            llm=function_llm,
            system_prompt=""" \
            Sie sind ein Experte für Wahlprogramme und helfen mir bei der Analyse.
            Bitte verwenden Sie immer die bereitgestellten Tools, um eine Frage zu beantworten. Verlassen Sie sich nicht auf Vorwissen.\
            """,
        )
        agents[program.id] = agent
        query_engines[program.id] = vector_index.as_query_engine(similarity_top_k=3)
        for tool in query_engine_tools:
            vector_tools.append(tool)

    logging.info(f"Loaded {len(vector_tools)} tools.")
    service_context = setup_service_context(model_version="3.5", azure=True)
    sub_question_query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=vector_tools,
        service_context=service_context,
    )
    query_engine_tool = QueryEngineTool(
        query_engine=sub_question_query_engine,
        metadata=ToolMetadata(
            name="sub_question_query_engine",
            description="Nützlich für Fragen, die mehrere Wahlprogramme betreffen.",
        ),
    )
    vector_tools.append(query_engine_tool)

    logging.info(f"Loaded query engine tool.")
    agent = OpenAIAgent.from_tools(
        vector_tools,
        llm=llm_35,
        system_prompt=""" \
        Sie sind ein Experte für Wahlprogramme und helfen mir bei der Analyse. Alle Fragen beziehen sich immer auf die Wahlprogramme der Parteien.
        Verwenden Sie immer die bereitgestellten Tools, um eine Frage zu beantworten. Verlassen Sie sich nicht auf Vorwissen.\
        """,
        verbose=True,
    )
    logging.info("Loaded agent.")
    return agent
