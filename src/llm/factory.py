"""LLM Provider Factory.

Returns the correct LangChain chat model based on LLM_PROVIDER env var.

Providers:
  ollama  - Free, local. Install Ollama + pull a model. Zero API cost.
  groq    - Free cloud tier. Fast. Get a free key at console.groq.com.
  bedrock - AWS Bedrock. Pay-per-token. Best for production/interview demo.

Usage:
    from src.llm.factory import get_llm
    llm = get_llm()           # uses LLM_PROVIDER env var
    llm = get_llm("ollama")   # explicit override
"""

import os
from typing import Literal

from langchain_core.language_models import BaseChatModel

Provider = Literal["ollama", "groq", "bedrock"]


def get_llm(
    provider: Provider | None = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
) -> BaseChatModel:
    """Return a configured LangChain chat model for the selected provider."""
    provider = provider or os.getenv("LLM_PROVIDER", "ollama")  # type: ignore

    if provider == "ollama":
        return _get_ollama(temperature, max_tokens)
    elif provider == "groq":
        return _get_groq(temperature, max_tokens)
    elif provider == "bedrock":
        return _get_bedrock(temperature, max_tokens)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose: ollama, groq, bedrock")


def _get_ollama(temperature: float, max_tokens: int) -> BaseChatModel:
    """Ollama — free local inference. https://ollama.com"""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        raise ImportError("Run: pip install langchain-ollama")

    model = os.getenv("OLLAMA_MODEL", "llama3.1")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(model=model, base_url=base_url, temperature=temperature, num_predict=max_tokens)


def _get_groq(temperature: float, max_tokens: int) -> BaseChatModel:
    """Groq — free cloud tier. https://console.groq.com"""
    try:
        from langchain_groq import ChatGroq
    except ImportError:
        raise ImportError("Run: pip install langchain-groq")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("Set GROQ_API_KEY in your .env file. Free key at console.groq.com")

    model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    return ChatGroq(api_key=api_key, model_name=model, temperature=temperature, max_tokens=max_tokens)


def _get_bedrock(temperature: float, max_tokens: int) -> BaseChatModel:
    """AWS Bedrock — pay-per-token. Requires AWS credentials configured."""
    try:
        from langchain_aws import ChatBedrock
    except ImportError:
        raise ImportError("Run: pip install langchain-aws")

    model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    return ChatBedrock(
        model_id=model_id,
        region_name=region,
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens},
    )
