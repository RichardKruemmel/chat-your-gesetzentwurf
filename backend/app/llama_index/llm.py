import logging
import os
from dotenv import load_dotenv
from llama_index import OpenAIEmbedding, ServiceContext
from llama_index.llms import AzureOpenAI, ChatMessage, OpenAI
from llama_index.embeddings import AzureOpenAIEmbedding

load_dotenv()
api_base = os.getenv("OPENAI_API_BASE")
api_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("OPENAI_API_VERSION")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
deployment_name_2 = os.getenv("OPENAI_DEPLOYMENT_NAME_2")
open_ai_api_key = os.getenv("OPENAI_WAHLWAVE_API_KEY")


messages = [
    ChatMessage(
        role="system",
        content="Du bist ein Experte für Wahlprogramme und hilfst mir bei der Analyse.",
    ),
    ChatMessage(role="user", content="Hallo, was sind Kernthemen der Grünen?"),
]

llm_35 = AzureOpenAI(
    engine=deployment_name,
    api_key=api_key,
    azure_endpoint=api_base,
    api_version=api_version,
    model="gpt-35-turbo",
)
llm_40 = AzureOpenAI(
    engine=deployment_name_2,
    api_key=api_key,
    azure_endpoint=api_base,
    api_version=api_version,
    model="gpt-4-32k",
)

ada_2 = AzureOpenAIEmbedding(
    api_key=api_key,
    azure_endpoint=api_base,
    api_version=api_version,
    model="text-embedding-ada-002",
    azure_deployment="wahlwave-embedding",
    embed_batch_size=16,
)

gpt_35 = OpenAI(api_key=open_ai_api_key, model="gpt-3", temperature=0.1)
ada_2_gpt = OpenAIEmbedding(api_key=open_ai_api_key, model="text-embedding-ada-002")


def verify_llm_connection():
    response_1 = llm_35.chat(messages)
    response_2 = llm_40.chat(messages)
    print(response_1)
    print(response_2)


def setup_service_context(model_version="3.5", azure=True):
    try:
        if model_version == "3.5" and azure:
            llm = llm_35
            embed_model = ada_2
        elif model_version == "4" and azure:
            llm = llm_40
            embed_model = ada_2
        elif not azure:
            llm = gpt_35
            embed_model = ada_2_gpt
        else:
            raise ValueError("Invalid model version specified")

        service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
        logging.info(f"Loaded service context for {model_version}.")
        return service_context
    except Exception as e:
        raise ValueError(f"Failed to set up service context: {e}")
