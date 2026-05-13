"""
RAGAS Metrics Definition
=========================
Initializes the 5 standard RAGAS metrics wired to the project's
evaluator LLM and embeddings.

Metric groups
-------------
CORE_METRICS   – faithfulness + answer_relevancy + context_recall
                 (no ground-truth required)
FULL_METRICS   – adds context_precision + answer_correctness
                 (requires 'reference' / ground-truth answers)
"""

from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextRecall,
    ContextPrecision,
    AnswerCorrectness,
)
from app.evaluation.config import eval_llm, eval_embeddings

# --------------------------------------------------------------------------
# Instantiate with the project's evaluator LLM / embeddings
# --------------------------------------------------------------------------
faithfulness = Faithfulness(llm=eval_llm)
answer_relevancy = AnswerRelevancy(llm=eval_llm, embeddings=eval_embeddings)
context_recall = ContextRecall(llm=eval_llm)
context_precision = ContextPrecision(llm=eval_llm)
answer_correctness = AnswerCorrectness(llm=eval_llm)

# Use CORE_METRICS when you don't have reference answers.
# Use FULL_METRICS once you have human-validated ground-truth.
CORE_METRICS = [faithfulness, answer_relevancy, context_recall]
FULL_METRICS = [
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    answer_correctness,
]
