from langchain.agents import initialize_agent
from langchain.agents import AgentType
from app.langchain.llm import chatgpt
from app.langchain.memory import memory, agent_kwargs

open_ai_agent = initialize_agent(
    chatgpt,
    agent=AgentType.RETRIEVAL_QA_WITH_SOURCES_CHAIN,
    memory=memory,
    agent_kwargs=agent_kwargs,
    return_intermediate_steps=True,
    verbose=True,
)
