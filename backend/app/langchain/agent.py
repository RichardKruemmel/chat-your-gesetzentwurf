from langchain.agents import initialize_agent
from langchain.agents import AgentType

from app.langchain.llm import chatgpt
from app.llama_index.tools import setup_agent_tools

llama_tools = setup_agent_tools()

open_ai_agent = initialize_agent(
    llm=chatgpt,
    agent=AgentType.OPENAI_FUNCTIONS,
    tools=llama_tools,
    verbose=True,
)
