import { useState } from "react";

const steps = [
  {
    id: 1,
    phase: "SETUP",
    title: "Install RAGAS & Dependencies",
    color: "#00D4AA",
    icon: "⚙️",
    description: "Install RAGAS alongside your existing stack. Your project uses uv, so these commands are tailored to it.",
    code: `# Inside backend/ directory
uv add ragas datasets langchain-google-genai

# Verify installation
uv run python -c "import ragas; print(ragas.__version__)"`,
    note: "RAGAS works best with Python 3.10+. Since you already have langchain + google-genai for embeddings, the overhead is minimal."
  },
  {
    id: 2,
    phase: "SETUP",
    title: "Create Evaluation Config File",
    color: "#00D4AA",
    icon: "📁",
    description: "Create a dedicated evaluation module in your backend. This keeps eval logic separate from your production agent code.",
    code: `# backend/app/evaluation/
# ├── __init__.py
# ├── config.py          ← LLM + embeddings for RAGAS
# ├── dataset_builder.py ← Harvest Q&A from your agents
# ├── run_eval.py        ← Main evaluation runner
# └── reports/           ← JSON/CSV output landing zone

# backend/app/evaluation/config.py
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os

# Use your EXISTING keys from backend/.env
eval_llm = LangchainLLMWrapper(
    GoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
)

eval_embeddings = LangchainEmbeddingsWrapper(
    GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
)`,
    note: "We reuse your existing Google Gemini keys. No new API costs unless you scale evaluation heavily."
  },
  {
    id: 3,
    phase: "DATA",
    title: "Build Your Evaluation Dataset",
    color: "#7C3AED",
    icon: "🗂️",
    description: "This is the most critical step. You need triplets of (question, answer, contexts). Hook into your FastAPI pipeline to harvest these automatically.",
    code: `# backend/app/evaluation/dataset_builder.py
from datasets import Dataset
from app.agents.graph import run_research_pipeline  # your LangGraph entry
from app.services.rag import retrieve_documents      # your Qdrant retriever
import json, asyncio

# --- OPTION A: Automatic harvesting from existing conversations ---
# Pull from PostgreSQL conversation history (you already store this!)
async def build_dataset_from_history(db_session, limit=100):
    rows = await db_session.execute(
        "SELECT question, answer, retrieved_chunks FROM conversations LIMIT %s",
        (limit,)
    )
    samples = []
    for row in rows:
        samples.append({
            "user_input":   row["question"],
            "response":     row["answer"],
            "retrieved_contexts": json.loads(row["retrieved_chunks"]),
            # RAGAS calls these: user_input, response, retrieved_contexts
        })
    return Dataset.from_list(samples)

# --- OPTION B: Synthetic test set (best for fresh evaluation) ---
SEED_QUESTIONS = [
    "What are the key findings in the uploaded research document?",
    "Summarize the methodology section of the paper.",
    "What limitations does the author mention?",
    "Compare the results from section 3 and section 5.",
    "What future work does the paper recommend?",
]

async def build_synthetic_dataset():
    samples = []
    for q in SEED_QUESTIONS:
        # Run your actual multi-agent pipeline
        result = await run_research_pipeline(question=q)
        
        # Grab retrieved chunks from Qdrant (your RAG agent step)
        contexts = await retrieve_documents(query=q, top_k=5)
        
        samples.append({
            "user_input":          q,
            "response":            result["final_answer"],
            "retrieved_contexts":  [c.page_content for c in contexts],
            "reference":           result.get("ground_truth", ""),  # optional
        })
    return Dataset.from_list(samples)`,
    note: "Since you have PostgreSQL storing conversation history, Option A lets you evaluate production traffic. Start with 50–100 pairs for meaningful scores."
  },
  {
    id: 4,
    phase: "METRICS",
    title: "Choose Your RAGAS Metrics",
    color: "#EF4444",
    icon: "📊",
    description: "RAGAS has specific metrics for each part of your pipeline. For a multi-agent RAG system like yours, these 5 are the essential baseline.",
    metrics: [
      { name: "Faithfulness", desc: "Is the answer grounded in retrieved context? Catches hallucinations from your Ollama agent.", score: "0–1 (higher=better)", critical: true },
      { name: "Answer Relevancy", desc: "Does the answer actually address the question? Tests your synthesis agent quality.", score: "0–1 (higher=better)", critical: true },
      { name: "Context Recall", desc: "Did Qdrant retrieve ALL necessary chunks? Tests your RAG retrieval agent.", score: "0–1 (higher=better)", critical: true },
      { name: "Context Precision", desc: "Are retrieved chunks actually useful? Detects noisy retrieval from Qdrant.", score: "0–1 (higher=better)", critical: false },
      { name: "Answer Correctness", desc: "Factual match vs ground truth. Requires reference answers.", score: "0–1 (higher=better)", critical: false },
    ],
    code: `from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextRecall,
    ContextPrecision,
    AnswerCorrectness,
)
from app.evaluation.config import eval_llm, eval_embeddings

# Initialize with YOUR evaluator LLM + embeddings
faithfulness    = Faithfulness(llm=eval_llm)
answer_relevancy = AnswerRelevancy(llm=eval_llm, embeddings=eval_embeddings)
context_recall  = ContextRecall(llm=eval_llm)
context_precision = ContextPrecision(llm=eval_llm)
answer_correctness = AnswerCorrectness(llm=eval_llm)

CORE_METRICS = [faithfulness, answer_relevancy, context_recall]
FULL_METRICS  = [faithfulness, answer_relevancy, context_recall,
                 context_precision, answer_correctness]`,
    note: "Start with CORE_METRICS (no ground truth needed). Add answer_correctness once you have human-validated reference answers."
  },
  {
    id: 5,
    phase: "RUN",
    title: "Run the Evaluation",
    color: "#F59E0B",
    icon: "🚀",
    description: "Execute RAGAS evaluation against your dataset. This calls your evaluator LLM (Gemini) to score each sample.",
    code: `# backend/app/evaluation/run_eval.py
import asyncio, json
from pathlib import Path
from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset
from datasets import Dataset
from app.evaluation.config import eval_llm, eval_embeddings
from app.evaluation.metrics import CORE_METRICS
from app.evaluation.dataset_builder import build_synthetic_dataset

async def run_full_evaluation():
    print("🔨 Building evaluation dataset...")
    hf_dataset = await build_synthetic_dataset()
    
    # Convert to RAGAS EvaluationDataset format
    eval_dataset = EvaluationDataset.from_hf_dataset(hf_dataset)
    
    print(f"📊 Evaluating {len(hf_dataset)} samples with RAGAS...")
    results = evaluate(
        dataset=eval_dataset,
        metrics=CORE_METRICS,
        llm=eval_llm,
        embeddings=eval_embeddings,
        show_progress=True,  # nice progress bar
        raise_exceptions=False,  # don't crash on a single bad sample
    )
    
    # ── Save results ──
    df = results.to_pandas()
    output_dir = Path("app/evaluation/reports")
    output_dir.mkdir(exist_ok=True)
    
    df.to_csv(output_dir / "latest_eval.csv", index=False)
    
    summary = {
        "faithfulness":     round(results["faithfulness"], 4),
        "answer_relevancy": round(results["answer_relevancy"], 4),
        "context_recall":   round(results["context_recall"], 4),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    
    print("\\n✅ EVALUATION COMPLETE")
    print(json.dumps(summary, indent=2))
    return results

if __name__ == "__main__":
    asyncio.run(run_full_evaluation())`,
    note: "Run from backend/: `uv run python -m app.evaluation.run_eval`. Each sample makes 2–3 LLM calls to Gemini, so 50 samples ≈ 150 API calls."
  },
  {
    id: 6,
    phase: "RUN",
    title: "Add RAGAS FastAPI Endpoint",
    color: "#F59E0B",
    icon: "🔌",
    description: "Expose evaluation as an API endpoint so you can trigger it from your frontend or CI/CD pipeline without dropping into the container.",
    code: `# backend/app/api/eval_router.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.evaluation.run_eval import run_full_evaluation
import json
from pathlib import Path

router = APIRouter(prefix="/eval", tags=["evaluation"])

@router.post("/run")
async def trigger_evaluation(background_tasks: BackgroundTasks):
    """Trigger async RAGAS evaluation — runs in background."""
    background_tasks.add_task(run_full_evaluation)
    return {"status": "evaluation started", "check": "/eval/results"}

@router.get("/results")
async def get_latest_results():
    """Fetch the last evaluation summary."""
    summary_path = Path("app/evaluation/reports/summary.json")
    if not summary_path.exists():
        raise HTTPException(404, "No evaluation run yet. POST /eval/run first.")
    return json.loads(summary_path.read_text())

# In app/main.py, register the router:
# from app.api.eval_router import router as eval_router
# app.include_router(eval_router)`,
    note: "Now you can curl -X POST http://localhost:8001/eval/run to kick off evaluation and GET /eval/results to see scores."
  },
  {
    id: 7,
    phase: "ADVANCED",
    title: "Per-Agent RAGAS Tracing",
    color: "#3B82F6",
    icon: "🔍",
    description: "Your LangGraph pipeline has 4 specialized agents. Evaluate each one separately to pinpoint exactly which agent is underperforming.",
    code: `# backend/app/evaluation/agent_eval.py
# Evaluate EACH agent in your pipeline independently

# 1. Research Agent → Answer Relevancy + Faithfulness
# 2. RAG Agent → Context Recall + Context Precision  
# 3. Synthesis Agent → Faithfulness (does it hallucinate?)
# 4. Critique Agent → Answer Correctness

from ragas.metrics import AnswerRelevancy, Faithfulness, ContextRecall
from datasets import Dataset
from ragas import evaluate

async def evaluate_rag_agent(qdrant_service, questions: list[str]):
    """Evaluate ONLY the Qdrant RAG retrieval step."""
    samples = []
    for q in questions:
        contexts = await qdrant_service.retrieve(q, top_k=5)
        samples.append({
            "user_input": q,
            "retrieved_contexts": [c.page_content for c in contexts],
            "response": "N/A",  # not needed for context metrics
            "reference": "",
        })
    
    dataset = Dataset.from_list(samples)
    results = evaluate(
        dataset=dataset,
        metrics=[ContextRecall(llm=eval_llm), ContextPrecision(llm=eval_llm)],
        llm=eval_llm,
    )
    return {
        "rag_agent": {
            "context_recall":    results["context_recall"],
            "context_precision": results["context_precision"],
            "verdict": "✅ Good" if results["context_recall"] > 0.75 else "⚠️ Improve chunking/embeddings"
        }
    }

async def evaluate_synthesis_agent(pipeline, questions: list[str]):
    """Evaluate ONLY the synthesis + critique agents."""
    samples = []
    for q in questions:
        result = await pipeline.run(q)
        samples.append({
            "user_input": q,
            "response": result["synthesized_answer"],
            "retrieved_contexts": result["contexts"],
        })
    
    dataset = Dataset.from_list(samples)
    results = evaluate(dataset=dataset, metrics=[Faithfulness(llm=eval_llm)], llm=eval_llm)
    return {
        "synthesis_agent": {
            "faithfulness": results["faithfulness"],
            "verdict": "✅ Good" if results["faithfulness"] > 0.80 else "⚠️ Agent is hallucinating"
        }
    }`,
    note: "This is where having a multi-agent system shines for evaluation — you can surgically identify whether retrieval, synthesis, or critique is your weakest link."
  },
  {
    id: 8,
    phase: "ADVANCED",
    title: "TestsetGenerator — Auto-Generate Test Cases",
    color: "#3B82F6",
    icon: "🤖",
    description: "RAGAS can synthesize test questions directly from your uploaded PDFs in Qdrant. No manual labeling needed.",
    code: `# backend/app/evaluation/testset_gen.py
from ragas.testset import TestsetGenerator
from langchain_community.document_loaders import PyPDFLoader
from app.evaluation.config import eval_llm, eval_embeddings

async def generate_testset_from_pdf(pdf_path: str, test_size: int = 25):
    """
    Auto-generate Q&A pairs from an uploaded PDF.
    Mirrors what your users actually upload to the RAG system.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    generator = TestsetGenerator(
        llm=eval_llm,
        embedding_model=eval_embeddings,
    )
    
    testset = generator.generate_with_langchain_docs(
        documents,
        testset_size=test_size,
        # Generates a mix of: simple, reasoning, multi-context questions
    )
    
    # Convert to HuggingFace Dataset
    hf_dataset = testset.to_pandas()
    print(f"✅ Generated {len(hf_dataset)} test cases from {pdf_path}")
    print(hf_dataset[["user_input", "reference"]].head())
    
    return testset

# Usage — run this once per new document type your users upload:
# uv run python -c "
# import asyncio
# from app.evaluation.testset_gen import generate_testset_from_pdf
# asyncio.run(generate_testset_from_pdf('sample_paper.pdf', test_size=30))
# "`,
    note: "Generate once, save to disk, reuse for every model/config change. This is how you build a regression suite that grows with your product."
  },
  {
    id: 9,
    phase: "CI",
    title: "Threshold Gates & CI Integration",
    color: "#10B981",
    icon: "🚦",
    description: "Set minimum score thresholds. If evaluation drops below them, your deployment pipeline fails. This prevents regressions from sneaking into production.",
    code: `# backend/app/evaluation/thresholds.py

SCORE_THRESHOLDS = {
    "faithfulness":     0.80,  # Below 0.80 = hallucination risk in prod
    "answer_relevancy": 0.75,  # Below 0.75 = answers off-topic
    "context_recall":   0.70,  # Below 0.70 = Qdrant missing key chunks
}

def check_thresholds(results: dict) -> tuple[bool, list[str]]:
    failures = []
    for metric, threshold in SCORE_THRESHOLDS.items():
        score = results.get(metric, 0)
        if score < threshold:
            failures.append(
                f"❌ {metric}: {score:.3f} < {threshold} (threshold)"
            )
    passed = len(failures) == 0
    return passed, failures

# In run_eval.py, add after evaluate():
# passed, failures = check_thresholds(summary)
# if not passed:
#     print("\\n🚨 EVALUATION FAILED:")
#     for f in failures: print(f)
#     sys.exit(1)  # Fails CI pipeline

# ── GitHub Actions integration ──────────────────────────
# .github/workflows/eval.yml:
#
# name: RAGAS Evaluation Gate
# on: [push, pull_request]
# jobs:
#   evaluate:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - name: Set up Python
#         uses: actions/setup-python@v5
#         with: { python-version: "3.11" }
#       - name: Install uv
#         run: pip install uv
#       - name: Install deps
#         run: cd backend && uv sync
#       - name: Run RAGAS eval
#         env:
#           GOOGLE_API_KEY: \${{ secrets.GOOGLE_API_KEY }}
#           QDRANT_API_KEY: \${{ secrets.QDRANT_API_KEY }}
#         run: |
#           cd backend
#           uv run python -m app.evaluation.run_eval`,
    note: "With this, every PR that degrades your RAG quality gets automatically caught before merging. Think of it as unit tests, but for AI quality."
  },
  {
    id: 10,
    phase: "CI",
    title: "Score Interpretation & Next Actions",
    color: "#10B981",
    icon: "🎯",
    description: "A cheat-sheet for reading RAGAS scores on your specific stack and knowing exactly what to fix.",
    scoreGuide: [
      { metric: "Faithfulness", low: "< 0.75", action: "Your Ollama gemma4 model is hallucinating. Try: stricter system prompts in your synthesis agent, or add a post-generation verification step." },
      { metric: "Answer Relevancy", low: "< 0.70", action: "Your research agent is drifting off-topic. Check LangGraph node routing logic and system prompts in agents/." },
      { metric: "Context Recall", low: "< 0.65", action: "Qdrant is missing relevant chunks. Tune: chunk_size, chunk_overlap, top_k, or switch embedding model." },
      { metric: "Context Precision", low: "< 0.60", action: "Qdrant is returning noisy/irrelevant chunks. Add metadata filtering or re-rank retrieved results." },
      { metric: "Answer Correctness", low: "< 0.65", action: "Factual errors in final output. Usually a synthesis or critique agent prompt issue. Strengthen your critique agent instructions." },
    ],
    note: "Run evaluation BEFORE and AFTER every major change (new model, new chunking strategy, new prompt). Track scores over time in your reports/ folder."
  },
];

const phaseColors = {
  SETUP: "#00D4AA",
  DATA: "#7C3AED",
  METRICS: "#EF4444",
  RUN: "#F59E0B",
  ADVANCED: "#3B82F6",
  CI: "#10B981",
};

const phaseLabels = {
  SETUP: "Setup",
  DATA: "Data Collection",
  METRICS: "Metrics Selection",
  RUN: "Running Eval",
  ADVANCED: "Advanced",
  CI: "CI/CD Gate",
};

export default function RagasGuide() {
  const [active, setActive] = useState(1);
  const [copiedCode, setCopiedCode] = useState(null);

  const current = steps.find(s => s.id === active);

  const copyCode = (code, id) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const phases = [...new Set(steps.map(s => s.phase))];

  return (
    <div style={{
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
      background: "#0A0E1A",
      minHeight: "100vh",
      color: "#E2E8F0",
      padding: "0",
      margin: "0",
    }}>
      {/* Header */}
      <div style={{
        background: "linear-gradient(135deg, #0D1426 0%, #111827 50%, #0A0E1A 100%)",
        borderBottom: "1px solid #1E2A3A",
        padding: "32px 40px 24px",
        position: "relative",
        overflow: "hidden",
      }}>
        <div style={{
          position: "absolute", top: 0, right: 0, width: "300px", height: "100%",
          background: "radial-gradient(circle at 80% 50%, rgba(0,212,170,0.08) 0%, transparent 70%)",
          pointerEvents: "none",
        }} />
        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "8px" }}>
          <div style={{
            background: "linear-gradient(135deg, #00D4AA, #7C3AED)",
            borderRadius: "12px", width: "48px", height: "48px",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "24px", flexShrink: 0,
          }}>📐</div>
          <div>
            <div style={{ fontSize: "11px", letterSpacing: "0.2em", color: "#00D4AA", textTransform: "uppercase", marginBottom: "4px" }}>
              MULTI_AGENT × RAGAS
            </div>
            <h1 style={{ margin: 0, fontSize: "22px", fontWeight: "700", color: "#F1F5F9" }}>
              Model Evaluation Playbook
            </h1>
          </div>
        </div>
        <p style={{ margin: "12px 0 0 0", color: "#94A3B8", fontSize: "13px", maxWidth: "700px", lineHeight: "1.6" }}>
          Complete step-by-step RAGAS integration for your LangGraph + Qdrant + Ollama + Gemini stack.
          Covers dataset harvesting, metric selection, per-agent evaluation, and CI/CD gates.
        </p>
      </div>

      <div style={{ display: "flex", height: "calc(100vh - 140px)", minHeight: "600px" }}>
        {/* Left Sidebar — Steps */}
        <div style={{
          width: "260px", flexShrink: 0,
          background: "#080C18",
          borderRight: "1px solid #1E2A3A",
          overflowY: "auto",
          padding: "16px 0",
        }}>
          {phases.map(phase => (
            <div key={phase} style={{ marginBottom: "4px" }}>
              <div style={{
                padding: "6px 20px",
                fontSize: "9px", letterSpacing: "0.18em", textTransform: "uppercase",
                color: phaseColors[phase], fontWeight: "700",
              }}>
                {phaseLabels[phase]}
              </div>
              {steps.filter(s => s.phase === phase).map(step => (
                <button key={step.id} onClick={() => setActive(step.id)} style={{
                  width: "100%", textAlign: "left", padding: "10px 20px",
                  background: active === step.id
                    ? `linear-gradient(90deg, ${step.color}18 0%, transparent 100%)`
                    : "transparent",
                  border: "none",
                  borderLeft: active === step.id ? `3px solid ${step.color}` : "3px solid transparent",
                  cursor: "pointer", color: active === step.id ? "#F1F5F9" : "#64748B",
                  fontSize: "12px", lineHeight: "1.4",
                  transition: "all 0.15s ease",
                }}>
                  <span style={{ marginRight: "8px" }}>{step.icon}</span>
                  <span style={{ fontWeight: active === step.id ? "600" : "400" }}>
                    Step {step.id}. {step.title}
                  </span>
                </button>
              ))}
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, overflowY: "auto", padding: "32px 40px" }}>
          {current && (
            <div>
              {/* Step Header */}
              <div style={{ display: "flex", alignItems: "flex-start", gap: "16px", marginBottom: "24px" }}>
                <div style={{
                  background: `${current.color}20`,
                  border: `1px solid ${current.color}40`,
                  borderRadius: "12px", width: "52px", height: "52px",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "24px", flexShrink: 0,
                }}>
                  {current.icon}
                </div>
                <div>
                  <div style={{
                    fontSize: "10px", letterSpacing: "0.15em",
                    color: current.color, textTransform: "uppercase",
                    fontWeight: "700", marginBottom: "4px",
                  }}>
                    Step {current.id} — {phaseLabels[current.phase]}
                  </div>
                  <h2 style={{ margin: 0, fontSize: "20px", fontWeight: "700", color: "#F1F5F9" }}>
                    {current.title}
                  </h2>
                </div>
              </div>

              {/* Description */}
              <p style={{
                color: "#94A3B8", fontSize: "14px", lineHeight: "1.7",
                marginBottom: "24px", maxWidth: "740px",
              }}>
                {current.description}
              </p>

              {/* Metrics Table (Step 4) */}
              {current.metrics && (
                <div style={{ marginBottom: "24px" }}>
                  <div style={{ fontSize: "11px", color: "#64748B", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "12px" }}>
                    Recommended Metrics for Your Stack
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    {current.metrics.map(m => (
                      <div key={m.name} style={{
                        background: "#0D1426",
                        border: `1px solid ${m.critical ? current.color + "40" : "#1E2A3A"}`,
                        borderRadius: "8px", padding: "12px 16px",
                        display: "flex", gap: "16px", alignItems: "flex-start",
                      }}>
                        <div style={{ width: "160px", flexShrink: 0 }}>
                          <span style={{
                            color: m.critical ? current.color : "#94A3B8",
                            fontWeight: "700", fontSize: "13px",
                          }}>
                            {m.name}
                          </span>
                          {m.critical && (
                            <span style={{
                              marginLeft: "6px", fontSize: "9px", background: current.color + "25",
                              color: current.color, padding: "1px 6px", borderRadius: "4px",
                              letterSpacing: "0.05em",
                            }}>CORE</span>
                          )}
                        </div>
                        <div style={{ flex: 1, color: "#94A3B8", fontSize: "12px", lineHeight: "1.5" }}>
                          {m.desc}
                        </div>
                        <div style={{ color: "#475569", fontSize: "11px", flexShrink: 0 }}>
                          {m.score}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Score Guide (Step 10) */}
              {current.scoreGuide && (
                <div style={{ marginBottom: "24px" }}>
                  <div style={{ fontSize: "11px", color: "#64748B", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "12px" }}>
                    Score Interpretation & Remediation
                  </div>
                  {current.scoreGuide.map(sg => (
                    <div key={sg.metric} style={{
                      background: "#0D1426", border: "1px solid #1E2A3A",
                      borderRadius: "8px", padding: "14px 16px", marginBottom: "8px",
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "6px" }}>
                        <span style={{ color: "#F1F5F9", fontWeight: "700", fontSize: "13px" }}>{sg.metric}</span>
                        <span style={{
                          background: "#EF444420", color: "#EF4444",
                          padding: "1px 8px", borderRadius: "4px", fontSize: "11px",
                        }}>{sg.low}</span>
                      </div>
                      <p style={{ margin: 0, color: "#94A3B8", fontSize: "12px", lineHeight: "1.6" }}>
                        {sg.action}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Code Block */}
              {current.code && (
                <div style={{ marginBottom: "20px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <div style={{ fontSize: "11px", color: "#64748B", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                      Code
                    </div>
                    <button onClick={() => copyCode(current.code, current.id)} style={{
                      background: copiedCode === current.id ? "#00D4AA20" : "#1E2A3A",
                      border: `1px solid ${copiedCode === current.id ? "#00D4AA60" : "#2D3A4A"}`,
                      borderRadius: "6px", padding: "4px 12px",
                      color: copiedCode === current.id ? "#00D4AA" : "#94A3B8",
                      fontSize: "11px", cursor: "pointer", transition: "all 0.2s",
                    }}>
                      {copiedCode === current.id ? "✓ Copied!" : "Copy"}
                    </button>
                  </div>
                  <div style={{
                    background: "#060A14",
                    border: "1px solid #1E2A3A",
                    borderRadius: "10px",
                    padding: "20px 24px",
                    overflowX: "auto",
                  }}>
                    <pre style={{
                      margin: 0, fontSize: "12px", lineHeight: "1.8",
                      color: "#CBD5E1", whiteSpace: "pre",
                    }}>
                      {current.code.split("\n").map((line, i) => {
                        const isComment = line.trim().startsWith("#");
                        const isKeyword = /^(from|import|async|def|class|return|if|for|await|with)\b/.test(line.trim());
                        const isString = line.includes("\"") || line.includes("'");
                        return (
                          <span key={i} style={{
                            display: "block",
                            color: isComment ? "#475569" : isKeyword ? "#7C3AED" : "#CBD5E1",
                          }}>
                            {line}
                          </span>
                        );
                      })}
                    </pre>
                  </div>
                </div>
              )}

              {/* Note */}
              {current.note && (
                <div style={{
                  background: `${current.color}10`,
                  border: `1px solid ${current.color}30`,
                  borderRadius: "8px", padding: "12px 16px",
                  display: "flex", gap: "10px", alignItems: "flex-start",
                }}>
                  <span style={{ color: current.color, fontSize: "14px", flexShrink: 0 }}>💡</span>
                  <p style={{ margin: 0, color: "#94A3B8", fontSize: "12px", lineHeight: "1.6" }}>
                    {current.note}
                  </p>
                </div>
              )}

              {/* Nav Buttons */}
              <div style={{ display: "flex", gap: "12px", marginTop: "32px" }}>
                {active > 1 && (
                  <button onClick={() => setActive(active - 1)} style={{
                    background: "#0D1426", border: "1px solid #2D3A4A",
                    borderRadius: "8px", padding: "10px 20px",
                    color: "#94A3B8", fontSize: "13px", cursor: "pointer",
                    transition: "all 0.15s",
                  }}>
                    ← Previous
                  </button>
                )}
                {active < steps.length && (
                  <button onClick={() => setActive(active + 1)} style={{
                    background: `linear-gradient(135deg, ${current.color}40, ${current.color}20)`,
                    border: `1px solid ${current.color}60`,
                    borderRadius: "8px", padding: "10px 20px",
                    color: "#F1F5F9", fontSize: "13px", cursor: "pointer",
                    fontWeight: "600", transition: "all 0.15s",
                  }}>
                    Next Step →
                  </button>
                )}
                {active === steps.length && (
                  <div style={{
                    background: "#00D4AA15", border: "1px solid #00D4AA40",
                    borderRadius: "8px", padding: "10px 20px",
                    color: "#00D4AA", fontSize: "13px", fontWeight: "600",
                  }}>
                    🎉 All steps complete!
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar — Progress */}
        <div style={{
          width: "220px", flexShrink: 0,
          background: "#080C18",
          borderLeft: "1px solid #1E2A3A",
          padding: "20px 16px",
          overflowY: "auto",
        }}>
          <div style={{ fontSize: "9px", letterSpacing: "0.15em", color: "#475569", textTransform: "uppercase", marginBottom: "16px" }}>
            Progress
          </div>
          <div style={{
            background: "#0D1426", borderRadius: "8px", padding: "12px",
            marginBottom: "16px", textAlign: "center",
          }}>
            <div style={{ fontSize: "28px", fontWeight: "700", color: "#F1F5F9" }}>
              {active}<span style={{ color: "#475569", fontSize: "16px" }}>/10</span>
            </div>
            <div style={{ fontSize: "11px", color: "#475569", marginTop: "4px" }}>Steps Complete</div>
            <div style={{
              height: "4px", background: "#1E2A3A", borderRadius: "2px", marginTop: "10px",
            }}>
              <div style={{
                height: "100%",
                width: `${(active / 10) * 100}%`,
                background: `linear-gradient(90deg, #00D4AA, #7C3AED)`,
                borderRadius: "2px",
                transition: "width 0.3s ease",
              }} />
            </div>
          </div>

          <div style={{ fontSize: "9px", letterSpacing: "0.15em", color: "#475569", textTransform: "uppercase", marginBottom: "12px" }}>
            Phases
          </div>
          {phases.map(phase => {
            const phaseSteps = steps.filter(s => s.phase === phase);
            const done = phaseSteps.filter(s => s.id < active).length;
            const total = phaseSteps.length;
            const isActive = phaseSteps.some(s => s.id === active);
            return (
              <div key={phase} style={{
                marginBottom: "10px",
                background: isActive ? `${phaseColors[phase]}10` : "transparent",
                border: `1px solid ${isActive ? phaseColors[phase] + "30" : "#1E2A3A"}`,
                borderRadius: "6px", padding: "8px 10px",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                  <span style={{ fontSize: "10px", color: isActive ? phaseColors[phase] : "#64748B", fontWeight: isActive ? "700" : "400" }}>
                    {phaseLabels[phase]}
                  </span>
                  <span style={{ fontSize: "10px", color: "#475569" }}>{done}/{total}</span>
                </div>
                <div style={{ height: "2px", background: "#1E2A3A", borderRadius: "1px" }}>
                  <div style={{
                    height: "100%", width: `${(done / total) * 100}%`,
                    background: phaseColors[phase], borderRadius: "1px",
                    transition: "width 0.3s ease",
                  }} />
                </div>
              </div>
            );
          })}

          <div style={{ marginTop: "24px", fontSize: "9px", color: "#475569", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: "10px" }}>
            Your Stack
          </div>
          {[
            { name: "LangGraph", status: "✓", color: "#00D4AA" },
            { name: "Qdrant", status: "✓", color: "#00D4AA" },
            { name: "Gemini Embed", status: "✓", color: "#00D4AA" },
            { name: "Ollama LLM", status: "✓", color: "#00D4AA" },
            { name: "FastAPI", status: "✓", color: "#00D4AA" },
            { name: "RAGAS", status: "→", color: "#F59E0B" },
          ].map(item => (
            <div key={item.name} style={{
              display: "flex", justifyContent: "space-between",
              padding: "5px 0", borderBottom: "1px solid #0F1825",
              fontSize: "11px",
            }}>
              <span style={{ color: "#64748B" }}>{item.name}</span>
              <span style={{ color: item.color, fontWeight: "700" }}>{item.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
