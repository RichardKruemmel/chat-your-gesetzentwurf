from langchain.agents import initialize_agent
from langchain.agents import AgentType

from app.langchain.llm import setup_chatgpt
from app.langchain.memory import memory
from app.llama_index.tools import setup_agent_tools


def setup_langchain_agent():
    llama_tools = setup_agent_tools()
    chatgpt = setup_chatgpt()
    langchain_agent = initialize_agent(
        llm=chatgpt,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        tools=llama_tools,
        verbose=True,
    )
    return langchain_agent
