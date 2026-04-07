"""LLM and embedding utilities for Azure OpenAI."""

import os
from langchain_openai import AzureChatOpenAI
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from dotenv import load_dotenv


def create_azure_embedding():
    """
    Create Azure OpenAI embeddings instance.
    
    Requires environment variables:
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_API_VERSION
        - AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    
    Returns:
        AzureOpenAIEmbeddings: Configured embeddings instance
        
    Raises:
        ValueError: If required environment variables are missing
        
    Example:
        >>> embeddings = create_azure_embedding()
        >>> vector = embeddings.embed_query("Hello world")
    """
    load_dotenv()
    
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    
    if not all([azure_openai_endpoint, azure_openai_api_key, azure_openai_api_version, azure_openai_embedding_deployment]):
        raise ValueError("Missing required Azure OpenAI environment variables for embeddings")
    
    embedding = AzureOpenAIEmbeddings(
        azure_endpoint=azure_openai_endpoint,
        azure_deployment=azure_openai_embedding_deployment,
        openai_api_key=azure_openai_api_key,
        openai_api_version=azure_openai_api_version
    )
    
    return embedding


def create_azure_llm(deployment_type="chat", temperature=0.7):
    """
    Create Azure OpenAI LLM instance.
    
    Args:
        deployment_type: Type of deployment to use ("chat" or "audio").
                        Defaults to "chat".
        temperature: Sampling temperature (0-1). Controls randomness of responses.
                    Defaults to 0.7.
    
    Returns:
        AzureChatOpenAI: Configured language model instance
        
    Raises:
        ValueError: If required environment variables are missing
        
    Environment Variables Required:
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_API_VERSION
        - AZURE_OPENAI_{DEPLOYMENT_TYPE}_DEPLOYMENT
        
    Example:
        >>> from setup_utils import create_azure_llm
        >>> llm = create_azure_llm()
        >>> response = llm.invoke("Hello, how are you?")
        >>> print(response.content)
        
    Example with custom settings:
        >>> llm = create_azure_llm(temperature=0.3)  # More deterministic
    """
    load_dotenv()
    
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    azure_openai_deployment = os.getenv(f"AZURE_OPENAI_{deployment_type.upper()}_DEPLOYMENT")

    if not azure_openai_endpoint or not azure_openai_api_key:
        raise ValueError("Missing Azure OpenAI endpoint or API key in environment variables.")

    if not azure_openai_deployment:
        raise ValueError(f"Missing AZURE_OPENAI_{deployment_type.upper()}_DEPLOYMENT in environment variables.")

    print(f"Creating Azure OpenAI LLM")
    print(f"  Deployment: {azure_openai_deployment}")
    print(f"  Endpoint: {azure_openai_endpoint}")
    print(f"  API Version: {azure_openai_api_version}")
    print(f"  Temperature: {temperature}")

    llm = AzureChatOpenAI(
        api_key=azure_openai_api_key,
        azure_endpoint=azure_openai_endpoint,
        azure_deployment=azure_openai_deployment,
        api_version=azure_openai_api_version,
        temperature=temperature
    )

    return llm
