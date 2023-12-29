import logging
import os
from dotenv import load_dotenv
from llama_index import OpenAIEmbedding, ServiceContext
from llama_index.llms import AzureOpenAI, ChatMessage, OpenAI
from llama_index.embeddings import AzureOpenAIEmbedding

from app.utils.env import get_env_variable


messages = [
    ChatMessage(
        role="system",
        content="Du bist ein Experte für Wahlprogramme und hilfst mir bei der Analyse.",
    ),
    ChatMessage(role="user", content="Hallo, wer bist du?"),
]


def setup_llm_35():
    azure_endpoint = get_env_variable("AZURE_OPENAI_ENDPOINT")
    api_key = get_env_variable("AZURE_OPENAI_API_KEY")
    api_version = get_env_variable("OPENAI_API_VERSION")
    deployment_name = get_env_variable("OPENAI_DEPLOYMENT_NAME")
    deployment_name_2 = get_env_variable("OPENAI_DEPLOYMENT_NAME_2")

    llm_35 = AzureOpenAI(
        engine=deployment_name,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        model="gpt-35-turbo",
    )
    return llm_35


def setup_llm_40():
    azure_endpoint = get_env_variable("AZURE_OPENAI_ENDPOINT")
    api_key = get_env_variable("AZURE_OPENAI_API_KEY")
    api_version = get_env_variable("OPENAI_API_VERSION")
    deployment_name_2 = get_env_variable("OPENAI_DEPLOYMENT_NAME_2")

    llm_40 = AzureOpenAI(
        engine=deployment_name_2,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        model="gpt-4-32k",
    )
    return llm_40


def setup_ada_2():
    azure_endpoint = get_env_variable("AZURE_OPENAI_ENDPOINT")
    api_key = get_env_variable("AZURE_OPENAI_API_KEY")
    api_version = get_env_variable("OPENAI_API_VERSION")

    ada_2 = AzureOpenAIEmbedding(
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        model="text-embedding-ada-002",
        azure_deployment="wahlwave-embedding",
        embed_batch_size=16,
    )
    return ada_2


def setup_gpt_35():
    openai_api_key = get_env_variable("OPENAI_WAHLWAVE_API_KEY")
    gpt_35 = OpenAI(api_key=openai_api_key, model="gpt-3", temperature=0.1)
    return gpt_35


def setup_ada_2_gpt():
    openai_api_key = get_env_variable("OPENAI_WAHLWAVE_API_KEY")
    ada_2_gpt = OpenAIEmbedding(api_key=openai_api_key, model="text-embedding-ada-002")
    return ada_2_gpt


def verify_llm_connection():
    llm_35 = setup_llm_35()
    llm_40 = setup_llm_40()
    response_1 = llm_35.chat(messages)
    response_2 = llm_40.chat(messages)
    print(response_1)
    print(response_2)


def setup_service_context(model_version="3.5", azure=True):
    try:
        if model_version == "3.5" and azure:
            llm = setup_llm_35()
            embed_model = setup_ada_2()
        elif model_version == "4" and azure:
            llm = setup_llm_40()
            embed_model = setup_ada_2()
        elif not azure:
            llm = setup_gpt_35()
            embed_model = setup_ada_2_gpt()
        else:
            raise ValueError("Invalid model version specified")

        service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
        logging.info(f"Loaded service context for {model_version}.")
        return service_context
    except Exception as e:
        raise ValueError(f"Failed to set up service context: {e}")
