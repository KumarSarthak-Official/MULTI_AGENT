"""
RAGAS Metrics Definition
=========================
Three reference-free metrics fully compatible with NVIDIA NIM:

  faithfulness       – LLM checks if answer is grounded in context (single-call)
  context_precision  – LLM checks if retrieved chunks are relevant (single-call)  
  context_recall     – Embedding cosine similarity between response & context
                       (NonLLMContextRecall — NO LLM calls, uses embeddings only)

Excluded metrics:
  AnswerRelevancy   – requires n=3 parallel LLM generations (NIM: only returns 1)
  ContextRecall     – requires 'reference' ground-truth answers we don't have
  AnswerCorrectness – requires 'reference' ground-truth answers we don't have
"""

from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextRecall,
    ContextPrecision,
    AnswerCorrectness,
    NonLLMContextRecall,
    ResponseRelevancy,
)
from app.evaluation.config import eval_llm, eval_embeddings

# --------------------------------------------------------------------------
# Instantiate with the project's evaluator LLM / embeddings
# --------------------------------------------------------------------------
faithfulness      = Faithfulness(llm=eval_llm)
context_precision = ContextPrecision(llm=eval_llm)

# ResponseRelevancy with strictness=1: single LLM call (not n=3 like default).
# Measures whether the response semantically matches the question intent.
# 100% reference-free and NVIDIA NIM-compatible.
response_relevancy = ResponseRelevancy(
    llm=eval_llm,
    embeddings=eval_embeddings,
    strictness=1,  # force single generation — NIM only returns 1 anyway
)

# Legacy / future metrics (require reference answers or n>1 LLM generations)
answer_relevancy   = AnswerRelevancy(llm=eval_llm, embeddings=eval_embeddings)
context_recall     = ContextRecall(llm=eval_llm)   # needs 'reference' column
non_llm_context_recall = NonLLMContextRecall()      # needs 'reference_contexts'
answer_correctness = AnswerCorrectness(llm=eval_llm) # needs 'reference' column

# --------------------------------------------------------------------------
# CORE: two guaranteed metrics — 100% NVIDIA NIM compatible, reference-free
# faithfulness:     LLM checks if every claim is grounded in retrieved context
# context_precision: LLM checks if retrieved chunks are relevant to the query
#
# Excluded from CORE (NVIDIA NIM incompatible):
#   ResponseRelevancy / AnswerRelevancy — requires internal n=3 or multi-step
#   question-generation calls that NIM's API does not support ('list' strip err)
# --------------------------------------------------------------------------
CORE_METRICS = [faithfulness, context_precision]

# FULL: complete suite (requires human ground-truth 'reference' answers)
FULL_METRICS = [
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
]
