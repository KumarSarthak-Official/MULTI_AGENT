"""
Evaluation FastAPI Router
==========================
Exposes two endpoints:
  POST /eval/run     – kick off a RAGAS evaluation in the background
  GET  /eval/results – fetch the latest summary.json
  GET  /eval/report  – fetch the per-sample CSV as JSON rows

Register in app/main.py with:
    from app.api.eval_router import router as eval_router
    app.include_router(eval_router)
"""

import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

from app.evaluation.run_eval import run_full_evaluation, REPORTS_DIR

router = APIRouter(prefix="/eval", tags=["evaluation"])


class EvalRequest(BaseModel):
    questions: list[str] | None = None
    use_documents: bool = True


# --------------------------------------------------------------------------
# POST /eval/run  —  trigger async evaluation
# --------------------------------------------------------------------------
@router.post("/run", summary="Trigger RAGAS evaluation (runs in background)")
async def trigger_evaluation(
    payload: EvalRequest,
    background_tasks: BackgroundTasks,
):
    """
    Starts the full RAGAS evaluation pipeline as a background task.
    Poll GET /eval/results to check when scores are available.
    """
    background_tasks.add_task(
        run_full_evaluation,
        questions=payload.questions,
        use_documents=payload.use_documents,
        fail_on_threshold=False,
    )
    return {
        "status": "evaluation started",
        "samples": len(payload.questions) if payload.questions else "default (5)",
        "check_results_at": "/eval/results",
    }


# --------------------------------------------------------------------------
# GET /eval/results  —  latest aggregated summary
# --------------------------------------------------------------------------
@router.get("/results", summary="Get latest RAGAS evaluation summary")
async def get_latest_results():
    """Returns the aggregated metric scores from the most recent eval run."""
    summary_path = REPORTS_DIR / "summary.json"
    if not summary_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No evaluation run yet. POST /eval/run first.",
        )
    return json.loads(summary_path.read_text())


# --------------------------------------------------------------------------
# GET /eval/report  —  per-sample CSV as JSON
# --------------------------------------------------------------------------
@router.get("/report", summary="Get per-sample RAGAS scores as JSON")
async def get_detailed_report(max_rows: int = Query(default=100, le=500)):
    """Returns per-sample scores from the latest evaluation CSV."""
    csv_path = REPORTS_DIR / "latest_eval.csv"
    if not csv_path.exists():
        raise HTTPException(
            status_code=404,
            detail="No evaluation CSV found. POST /eval/run first.",
        )

    import csv

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(row)

    return {"total_rows": len(rows), "rows": rows}
