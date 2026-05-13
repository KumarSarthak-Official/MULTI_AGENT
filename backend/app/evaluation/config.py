"""
RAGAS Evaluation Configuration
================================
Uses NVIDIA NIM API for both the evaluator LLM and embeddings.

LLM:        nvidia/nemotron-3-super-120b-a12b  (Nemotron 3 Super)
Embeddings: nvidia/llama-nemotron-embed-1b-v2   (NVIDIA's dedicated embed model)

Both are accessed via NVIDIA's OpenAI-compatible endpoint:
    https://integrate.api.nvidia.com/v1

The NVIDIA_API_KEY is stored in backend/.env.
Fallback: Gemini embeddings are kept if NVIDIA embeddings ever fail.
"""

import os
from dotenv import load_dotenv
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

_nvidia_key = os.getenv("NVIDIA_API_KEY")
if not _nvidia_key:
    raise EnvironmentError(
        "NVIDIA_API_KEY is not set. Add it to backend/.env"
    )

_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# ---------------------------------------------------------------------------
# Evaluator LLM — Nemotron Nano 8B (fast, fits NVIDIA's 120s server timeout)
# The 120B Super model is too slow for RAGAS's multi-step LLM-as-judge prompts.
# Nano 8B responds in 2-5s per request vs 90-120s for the 120B Super model.
# Switch back to nemotron-3-super-120b-a12b after NVIDIA increases timeout limits.
# ---------------------------------------------------------------------------
eval_llm = LangchainLLMWrapper(
    ChatOpenAI(
        model="nvidia/llama-3.1-nemotron-nano-8b-v1",
        base_url=_NVIDIA_BASE_URL,
        api_key=_nvidia_key,
        temperature=0,
    )
)

# ---------------------------------------------------------------------------
# Evaluator Embeddings — NVIDIA llama-nemotron-embed-1b-v2
# Dedicated embedding model available on the same NIM endpoint.
# ---------------------------------------------------------------------------
eval_embeddings = LangchainEmbeddingsWrapper(
    OpenAIEmbeddings(
        model="nvidia/llama-nemotron-embed-1b-v2",
        base_url=_NVIDIA_BASE_URL,
        api_key=_nvidia_key,
    )
)
