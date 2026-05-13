"""
RAGAS Evaluation Runner
=========================
Main evaluation entry point.

Usage (from backend/ directory):
    uv run python -m app.evaluation.run_eval

Or with a custom question list:
    uv run python -m app.evaluation.run_eval --questions "Q1" "Q2"

Outputs
-------
  app/evaluation/reports/latest_eval.csv   – per-sample scores
  app/evaluation/reports/summary.json      – aggregated scores
"""

import asyncio
import json
import sys
import math
import argparse
from pathlib import Path

from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.dataset_schema import EvaluationDataset

from app.evaluation.config import eval_llm, eval_embeddings
from app.evaluation.metrics import CORE_METRICS
from app.evaluation.dataset_builder import build_synthetic_dataset, SEED_QUESTIONS
from app.evaluation.thresholds import check_thresholds


REPORTS_DIR = Path("app/evaluation/reports")


def _safe_float(val) -> float | None:
    """Safely convert a RAGAS result value to float (handles NaN/lists)."""
    if val is None:
        return None
    if isinstance(val, list):
        nums = [v for v in val if v is not None and not (isinstance(v, float) and math.isnan(v))]
        return round(sum(nums) / len(nums), 4) if nums else None
    try:
        f = float(val)
        return None if math.isnan(f) else round(f, 4)
    except (TypeError, ValueError):
        return None


async def run_full_evaluation(
    questions: list[str] | None = None,
    use_documents: bool = True,
    fail_on_threshold: bool = False,
) -> dict:
    """
    Build dataset → evaluate with RAGAS → save results.

    Args:
        questions:         Override default SEED_QUESTIONS.
        use_documents:     Whether to enable the RAG agent.
        fail_on_threshold: Exit with code 1 if scores fall below thresholds
                           (useful for CI gates).

    Returns:
        Dict with aggregated metric scores.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Build dataset ────────────────────────────────────────────────────
    print("🔨  Building evaluation dataset …")
    hf_dataset = await build_synthetic_dataset(
        questions=questions,
        use_documents=use_documents,
    )
    print(f"✅  Dataset built: {len(hf_dataset)} samples")

    if len(hf_dataset) == 0:
        print("❌  No samples in dataset. Aborting.")
        sys.exit(1)

    # ── 2. Convert to RAGAS EvaluationDataset ───────────────────────────────
    eval_dataset = EvaluationDataset.from_hf_dataset(hf_dataset)

    # ── 3. Run RAGAS evaluate — one metric at a time to avoid rate limits ────
    # Firing all metrics at once = 15 concurrent API calls → NVIDIA 429 errors.
    # Running sequentially = 5 calls per metric, with a pause between batches.
    import time

    run_cfg = RunConfig(timeout=120, max_retries=3, max_wait=30)
    combined_df = None
    summary: dict[str, float] = {}

    for i, metric in enumerate(CORE_METRICS):
        print(f"\n📊  [{i+1}/{len(CORE_METRICS)}] Evaluating metric: {metric.name} …")
        try:
            result = evaluate(
                dataset=eval_dataset,
                metrics=[metric],
                llm=eval_llm,
                embeddings=eval_embeddings,
                show_progress=True,
                raise_exceptions=False,
                run_config=run_cfg,
            )
            metric_df = result.to_pandas()
            summary[metric.name] = _safe_float(result[metric.name])
            print(f"   → {metric.name}: {summary[metric.name]}")

            if combined_df is None:
                combined_df = metric_df
            else:
                # Merge the new metric column into the combined dataframe
                combined_df[metric.name] = metric_df[metric.name].values

        except Exception as e:
            print(f"   ⚠️  {metric.name} failed: {e}")
            summary[metric.name] = None

        # Pause between metrics to respect NVIDIA's rate limit
        if i < len(CORE_METRICS) - 1:
            print("   ⏳ Pausing 8s before next metric …")
            time.sleep(8)

    # ── 4. Save per-sample CSV ───────────────────────────────────────────────
    csv_path = REPORTS_DIR / "latest_eval.csv"
    if combined_df is not None:
        combined_df.to_csv(csv_path, index=False)
    print(f"\n📁  Per-sample results saved → {csv_path}")

    # ── 5. Save summary ──────────────────────────────────────────────────────
    summary_path = REPORTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    print(f"📁  Summary saved → {summary_path}")

    # ── 6. Print results ─────────────────────────────────────────────────────
    print("\n" + "═" * 50)
    print("  ✅  EVALUATION COMPLETE")
    print("═" * 50)
    print(json.dumps(summary, indent=2))

    # ── 7. Threshold check ───────────────────────────────────────────────────
    passed, failures = check_thresholds(summary, exit_on_failure=fail_on_threshold)
    if not passed and not fail_on_threshold:
        print("\n⚠️   Some metrics are below threshold (non-blocking):")
        for f in failures:
            print(f"     {f}")

    return summary


# ── CLI entrypoint ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run RAGAS evaluation against the Multi-Agent RAG pipeline."
    )
    parser.add_argument(
        "--questions",
        nargs="+",
        default=None,
        help="Override seed questions. Example: --questions 'Q1' 'Q2'",
    )
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Disable the RAG agent (web-search-only mode).",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Exit with code 1 if threshold gates fail (for CI pipelines).",
    )
    args = parser.parse_args()

    asyncio.run(
        run_full_evaluation(
            questions=args.questions,
            use_documents=not args.no_docs,
            fail_on_threshold=args.ci,
        )
    )
