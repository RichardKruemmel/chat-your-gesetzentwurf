import os
import openai
from dotenv import load_dotenv
from typing import Any
from langchain.chat_models import AzureChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain, LLMChain


load_dotenv()
openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
chatgpt = AzureChatOpenAI(deployment_name=deployment_name)


def create_chain(vectorstore: Any) -> LLMChain:
    try:
        retriever = vectorstore.as_retriever()
    except Exception as e:
        print(f"Error in converting vectorstore to retriever: {str(e)}")
        return None

    try:
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=chatgpt,
            chain_type="stuff",
            retriever=retriever,
        )
    except Exception as e:
        print(f"Error in creating the chain: {str(e)}")
        return None

    return chain
