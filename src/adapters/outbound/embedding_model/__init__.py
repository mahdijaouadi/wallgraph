# embedding_model/__init__.py
# Re-export helpers for convenience
from .google_genai_embeddings import (
    GoogleEmbeddings,
    GeminiEmbedding3072,
    GeminiEmbedding768,
)
__all__ = [
    "GoogleEmbeddings",
    "GeminiEmbedding3072",
    "GeminiEmbedding768",
]
