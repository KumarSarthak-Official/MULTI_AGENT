from app.agents.state import ResearchState
from app.services.llm_service import llm_service
from typing import Dict, Any


def synthesis_agent_node(state: ResearchState) -> Dict[str, Any]:
    """Synthesis Agent: Combines web and document sources into structured report.

    Process:
    1. Gather search results and RAG context
    2. Generate structured markdown report with sections:
       - Executive Summary
       - Key Findings
       - Detailed Analysis
       - Conclusion
       - Sources
    3. Return draft report

    Args:
        state: Current ResearchState

    Returns:
        Dict with updated draft_report, sources, and agent_logs
    """
    query = state["query"]
    search_results = state.get("search_results", [])
    rag_context = state.get("rag_context", [])
    iteration_count = state.get("iteration_count", 0)

    agent_logs = [f"Synthesis Agent: Starting report generation for '{query}'"]

    # Check if this is a refinement iteration
    if iteration_count > 0:
        agent_logs.append(
            f"Synthesis Agent: Refinement iteration {iteration_count}"
        )
        previous_critique = state.get("critique", {})
        feedback = previous_critique.get("feedback", "")
        agent_logs.append(f"Synthesis Agent: Applying feedback: {feedback[:100]}...")

    try:
        # Prepare context from sources
        web_context = prepare_web_context(search_results)
        doc_context = prepare_doc_context(rag_context)

        agent_logs.append(
            f"Synthesis Agent: Using {len(search_results)} web sources "
            f"and {len(rag_context)} document chunks"
        )

        # Generate report
        system_prompt = """You are a research report writer. Generate comprehensive, well-structured reports
that synthesize information from multiple sources. Use markdown formatting with clear sections.
Always cite sources with [1], [2], etc. and include a Sources section at the end."""

        prompt = f"""Generate a comprehensive research report on the following topic:

Topic: {query}

Web Sources:
{web_context}

Document Sources:
{doc_context}

Generate a report with these sections:
# {query}

## Executive Summary
[2-3 sentences summarizing key findings]

## Key Findings
[Bullet points of main discoveries]

## Detailed Analysis
[In-depth analysis with citations]

## Conclusion
[Summary and implications]

## Sources
[Numbered list of all sources cited]

Use inline citations like [1], [2] throughout the report."""

        # Add refinement context if this is a revision
        if iteration_count > 0:
            previous_draft = state.get("draft_report", "")
            critique_feedback = state.get("critique", {}).get("feedback", "")
            prompt += f"""

PREVIOUS DRAFT:
{previous_draft}

CRITIQUE FEEDBACK:
{critique_feedback}

Please revise the report addressing the feedback above."""

        agent_logs.append("Synthesis Agent: Generating report with LLM")
        draft_report = llm_service.generate(prompt, system_prompt)

        # Collect all sources
        sources = []
        for i, result in enumerate(search_results, 1):
            sources.append({
                "id": i,
                "type": "web",
                "title": result.get("title", ""),
                "url": result.get("url", ""),
            })

        for i, doc in enumerate(rag_context, len(search_results) + 1):
            sources.append({
                "id": i,
                "type": "document",
                "source": doc.get("source", ""),
                "page": doc.get("page", 0),
            })

        agent_logs.append(
            f"Synthesis Agent: Generated report with {len(sources)} sources"
        )

        return {
            "draft_report": draft_report,
            "sources": sources,
            "agent_logs": agent_logs,
        }

    except Exception as e:
        error_msg = f"Synthesis Agent: Error - {str(e)}"
        agent_logs.append(error_msg)
        return {
            "draft_report": "",
            "sources": [],
            "agent_logs": agent_logs,
            "error": error_msg,
        }


def prepare_web_context(search_results: list[dict]) -> str:
    """Format web search results for LLM context."""
    if not search_results:
        return "No web sources available."

    context = []
    for i, result in enumerate(search_results, 1):
        context.append(
            f"[{i}] {result.get('title', 'Untitled')}\n"
            f"URL: {result.get('url', '')}\n"
            f"Snippet: {result.get('snippet', '')}\n"
        )

    return "\n".join(context)


def prepare_doc_context(rag_context: list[dict]) -> str:
    """Format RAG document chunks for LLM context."""
    if not rag_context:
        return "No document sources available."

    context = []
    for i, doc in enumerate(rag_context, 1):
        context.append(
            f"[Doc {i}] Source: {doc.get('source', 'Unknown')}, "
            f"Page: {doc.get('page', 0)}\n"
            f"Text: {doc.get('text', '')}\n"
        )

    return "\n".join(context)
