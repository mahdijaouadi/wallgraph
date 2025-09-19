from __future__ import annotations

from dotenv import load_dotenv
from typing import List, Optional, Sequence
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
class AsyncGoogleEmbeddings:
    """
    Async wrapper around GoogleGenerativeAIEmbeddings.

    Example:
        emb = AsyncGoogleEmbeddings(
            model="models/embedding-001",
            output_dimensionality=768,
        )
        vec = await emb.embed_query("hello world")
        vecs = await emb.embed_documents(["a", "b"])
    """
    def __init__(
        self,
        model: str,
        output_dimensionality: Optional[int] = None,
        api_key_env: str = "GOOGLE_API_KEY",
    ) -> None:
        load_dotenv()
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"{api_key_env} not found in environment")

        request_options = None
        if output_dimensionality is not None:
            request_options = {"output_dimensionality": int(output_dimensionality)}

        self._emb = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=api_key,
            request_options=request_options,
        )

    async def embed_query(self, text: str) -> List[float]:
        """Async: embed a single string."""
        return self._emb.embed_query(text)

    async def embed_documents(self, texts: list[str]) -> List[List[float]]:
        """Async: embed a batch of strings."""
        return self._emb.embed_documents(texts)

    async def aembed_query(self, text: str) -> List[float]:
        return await self._emb.aembed_query(text)

    async def aembed_documents(self, texts: list[str]) -> List[List[float]]:
        return await self._emb.aembed_documents(texts)

    # ---- No-op async context manager (optional) ----
    async def __aenter__(self) -> "AsyncGoogleEmbeddings":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None  # nothing to clean up

    @property
    def raw(self) -> GoogleGenerativeAIEmbeddings:
        """Access the underlying LangChain embeddings object (sync)."""
        return self._emb


def GeminiEmbedding3072Async() -> AsyncGoogleEmbeddings:
    """
    Factory for Gemini experimental 3,072-dim embeddings.

    Model: models/gemini-embedding-exp-03-07
    Dimensionality: 3072
    """
    return AsyncGoogleEmbeddings(
        model="models/gemini-embedding-exp-03-07",
        output_dimensionality=3072,
    )


def GeminiEmbedding768Async() -> AsyncGoogleEmbeddings:
    """
    Factory for Gemini 768-dim embeddings.

    Model: models/embedding-001
    Dimensionality: 768
    """
    return AsyncGoogleEmbeddings(
        model="models/embedding-001",
        output_dimensionality=768,
    )
