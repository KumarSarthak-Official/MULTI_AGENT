"""
Quick smoke-test: verify the evaluation pipeline works end-to-end
with a minimal 1-question dataset (avoids burning too many API calls).

Run from backend/:
    uv run python app/evaluation/quick_test.py
"""

import sys
import asyncio
import math
sys.stdout.reconfigure(encoding="utf-8")

from datasets import Dataset
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.dataset_schema import EvaluationDataset
from app.evaluation.config import eval_llm, eval_embeddings
from app.evaluation.metrics import CORE_METRICS
from app.evaluation.thresholds import check_thresholds


def _safe_float(val) -> float | None:
    """Extract a float from a RAGAS result value (handles NaN, lists, None)."""
    if val is None:
        return None
    if isinstance(val, list):
        # RAGAS returns a list of per-sample scores on timeout
        nums = [v for v in val if v is not None and not (isinstance(v, float) and math.isnan(v))]
        return round(sum(nums) / len(nums), 4) if nums else None
    try:
        f = float(val)
        return None if math.isnan(f) else round(f, 4)
    except (TypeError, ValueError):
        return None


async def main():
    print("=" * 60)
    print("  RAGAS Quick Smoke Test")
    print("=" * 60)

    # Minimal hand-crafted sample — no pipeline call needed
    sample = [
        {
            "user_input": "What is retrieval-augmented generation?",
            "response": (
                "Retrieval-Augmented Generation (RAG) is an AI technique "
                "that combines a language model with an external knowledge "
                "retrieval system. The model first retrieves relevant documents "
                "from a vector store, then uses those documents as context when "
                "generating its answer, reducing hallucinations."
            ),
            "retrieved_contexts": [
                "RAG stands for Retrieval-Augmented Generation. "
                "It retrieves relevant passages from a document store and "
                "feeds them as context to a large language model.",
                "RAG helps language models stay factually grounded by "
                "anchoring responses in retrieved evidence rather than "
                "relying solely on parametric knowledge.",
            ],
            "reference": (
                "Retrieval-Augmented Generation is a method where an LLM "
                "retrieves relevant context from an external database before "
                "generating a response, improving factual accuracy."
            ),
        }
    ]

    hf_ds = Dataset.from_list(sample)
    eval_ds = EvaluationDataset.from_hf_dataset(hf_ds)

    print(f"\nRunning RAGAS on {len(hf_ds)} sample(s)...")
    results = evaluate(
        dataset=eval_ds,
        metrics=CORE_METRICS,
        llm=eval_llm,
        embeddings=eval_embeddings,
        show_progress=True,
        raise_exceptions=False,
        run_config=RunConfig(timeout=300, max_retries=2, max_wait=30),
    )

    summary = {m.name: _safe_float(results[m.name]) for m in CORE_METRICS}
    import json
    print("\n" + "=" * 60)
    print("  Results")
    print("=" * 60)
    print(json.dumps(summary, indent=2))

    passed, failures = check_thresholds(summary)
    if passed:
        print("\n[OK] All threshold gates passed!")
    else:
        print("\n[WARN] Threshold failures:")
        for f in failures:
            print("  " + f)

    print("\nSmoke test complete.")


if __name__ == "__main__":
    asyncio.run(main())
