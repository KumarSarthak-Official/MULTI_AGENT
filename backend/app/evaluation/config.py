"""
RAGAS Evaluation Configuration
================================
Reuses the existing GOOGLE_API_KEY from backend/.env.
Gemini Flash is used as the evaluator LLM and embedding model —
no additional API costs beyond what the main system already uses.
"""

import os
from dotenv import load_dotenv
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load .env from the backend root (works whether running inside or outside the container)
load_dotenv()

_api_key = os.getenv("GOOGLE_API_KEY")
if not _api_key:
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. "
        "Add it to backend/.env before running evaluation."
    )

# ---------------------------------------------------------------------------
# Evaluator LLM — Gemini 1.5 Flash (generous free-tier quota)
# Switch to gemini-2.0-flash if you have a paid plan or when quota resets.
#
# QUOTA NOTE: The free tier for gemini-2.0-flash allows ~50 RPD.
# If you see 429 RESOURCE_EXHAUSTED errors:
#   1. Wait until midnight PST (daily quota resets)
#   2. OR upgrade to a Gemini paid plan at https://aistudio.google.com
#   3. OR change the model below to "gemini-1.5-flash" (separate quota bucket)
# ---------------------------------------------------------------------------
_EVAL_MODEL = "gemini-2.0-flash"

eval_llm = LangchainLLMWrapper(
    GoogleGenerativeAI(
        model=_EVAL_MODEL,
        google_api_key=_api_key,
        temperature=0,  # deterministic scoring
    )
)

# ---------------------------------------------------------------------------
# Evaluator Embeddings — text-embedding-004 (stable free-tier model)
# ---------------------------------------------------------------------------
eval_embeddings = LangchainEmbeddingsWrapper(
    GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=_api_key,
    )
)
