from typing import Any
import os
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain, LLMChain

from app.utils.env import get_env_variable


def setup_chatgpt() -> AzureChatOpenAI:
    api_type = "azure"
    azure_endpoint = get_env_variable("AZURE_OPENAI_ENDPOINT")
    api_key = get_env_variable("AZURE_OPENAI_API_KEY")
    api_version = get_env_variable("OPENAI_API_VERSION")
    deployment_name = get_env_variable("OPENAI_DEPLOYMENT_NAME")
    chatgpt = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=deployment_name,
        api_key=api_key,
        api_version=api_version,
        openai_api_type=api_type,
    )
    return chatgpt


def create_chain(vectorstore: Any) -> LLMChain:
    try:
        retriever = vectorstore.as_retriever()
    except Exception as e:
        print(f"Error in converting vectorstore to retriever: {str(e)}")
        return None

    try:
        chatgpt = setup_chatgpt()
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=chatgpt,
            chain_type="stuff",
            retriever=retriever,
        )
    except Exception as e:
        print(f"Error in creating the chain: {str(e)}")
        return None

    return chain
