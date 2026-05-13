"""
Threshold Gates
================
Define minimum acceptable RAGAS scores for each metric.
If any metric falls below its threshold the evaluation run
exits with code 1 — blocking CI/CD pipelines.

Thresholds are conservative baselines; tighten them as
your system matures.
"""
import sys

SCORE_THRESHOLDS: dict[str, float] = {
    "faithfulness":      0.80,  # < 0.80 → hallucination risk in production
    "context_precision": 0.60,  # < 0.60 → retrieval returning noisy chunks
}


def check_thresholds(
    results: dict[str, float],
    exit_on_failure: bool = False,
) -> tuple[bool, list[str]]:
    """
    Compare metric scores against SCORE_THRESHOLDS.

    Args:
        results:         Dict mapping metric name → float score.
        exit_on_failure: If True, call sys.exit(1) when any threshold fails
                         (use this in CI scripts).

    Returns:
        (passed, failures) where failures is a list of human-readable
        failure descriptions.
    """
    failures: list[str] = []
    for metric, threshold in SCORE_THRESHOLDS.items():
        score = results.get(metric)
        if score is None:
            continue  # metric was not computed in this run
        if score < threshold:
            failures.append(
                f"[FAIL] {metric}: {score:.4f} < {threshold} (threshold)"
            )

    passed = len(failures) == 0

    if not passed and exit_on_failure:
        print("\n🚨  EVALUATION FAILED — threshold gates not met:")
        for f in failures:
            print(f"     {f}")
        sys.exit(1)

    return passed, failures
