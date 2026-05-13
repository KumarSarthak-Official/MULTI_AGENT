from app.agents.state import ResearchState
from app.services.llm_service import llm_service
from typing import Dict, Any
import re


def critique_agent_node(state: ResearchState) -> Dict[str, Any]:
    """Critique Agent: Evaluates draft report quality using LLM-as-Judge pattern.

    Process:
    1. Score draft on accuracy, completeness, citations, clarity (1-10)
    2. Provide detailed feedback
    3. If score < 7 and no refinements yet: trigger one refinement cycle
    4. If score >= 7 or refinements exhausted: finalize report

    Args:
        state: Current ResearchState

    Returns:
        Dict with updated critique, final_report, iteration_count, and agent_logs
    """
    draft_report = state.get("draft_report", "")
    iteration_count = state.get("iteration_count", 0)
    query = state["query"]

    agent_logs = [f"Critique Agent: Evaluating draft report for '{query}'"]

    if not draft_report:
        agent_logs.append("Critique Agent: No draft report to evaluate")
        return {
            "critique": {"score": 0, "feedback": "No draft report provided"},
            "final_report": "",
            "iteration_count": iteration_count + 1,
            "agent_logs": agent_logs,
            "error": "No draft report to critique",
        }

    try:
        # Generate critique using LLM-as-Judge
        system_prompt = """You are a research report evaluator. Score reports on a scale of 1-10.

Scoring criteria (apply in order):
1. GROUNDING (most important — worth 4 points):
   - Does every factual claim have an inline citation [1], [2] pointing to a listed source?
   - Are there any claims that appear to come from outside the provided sources (hallucinations)?
   - Deduct 2 points for each hallucinated or unsourced factual claim you identify.
   - Start with 4 points for this criterion and deduct accordingly.

2. CITATIONS (worth 2 points):
   - Are inline citations used consistently throughout?
   - Is there a complete Sources section?

3. COMPLETENESS (worth 2 points):
   - Are the major themes from the sources covered?

4. CLARITY (worth 2 points):
   - Is the report well-structured and clearly written?

Format your response EXACTLY as:
SCORE: [number 1-10]
HALLUCINATIONS: [list any claims not supported by sources, or "None found"]
FEEDBACK: [detailed feedback on all criteria]"""

        prompt = f"""Evaluate this research report:

Topic: {query}

Report:
{draft_report}

Provide your evaluation with SCORE and FEEDBACK."""

        agent_logs.append("Critique Agent: Generating evaluation with LLM")
        response = llm_service.generate(prompt, system_prompt)

        # Parse score and feedback
        score, feedback = parse_critique_response(response)
        agent_logs.append(f"Critique Agent: Score = {score}/10")

        critique = {"score": score, "feedback": feedback}

        # Decision logic
        if iteration_count >= 1:
            # Max refinements reached (1 cycle), finalize regardless of score
            agent_logs.append(
                "Critique Agent: Max refinements reached, finalizing report"
            )
            return {
                "critique": critique,
                "final_report": draft_report,
                "iteration_count": iteration_count + 1,
                "agent_logs": agent_logs,
            }

        if score < 7:
            # Request one refinement cycle
            agent_logs.append(
                "Critique Agent: Score below threshold (7), requesting refinement"
            )
            return {
                "critique": critique,
                "iteration_count": iteration_count + 1,
                "agent_logs": agent_logs,
            }

        # Score is good, finalize
        agent_logs.append(
            "Critique Agent: Score meets threshold, finalizing report"
        )
        return {
            "critique": critique,
            "final_report": draft_report,
            "agent_logs": agent_logs,
        }

    except Exception as e:
        error_msg = f"Critique Agent: Error - {str(e)}"
        agent_logs.append(error_msg)
        # On error, finalize with current draft to avoid infinite loop
        return {
            "critique": {"score": 5, "feedback": f"Error during critique: {str(e)}"},
            "final_report": draft_report,
            "iteration_count": iteration_count + 1,
            "agent_logs": agent_logs,
            "error": error_msg,
        }


def parse_critique_response(response: str) -> tuple[int, str]:
    """Parse LLM critique response to extract score and feedback.

    Args:
        response: LLM response text

    Returns:
        Tuple of (score, feedback)
    """
    try:
        # Try to extract SCORE: [number]
        score_match = re.search(r"SCORE:\s*(\d+)", response, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            # Clamp to 1-10 range
            score = max(1, min(10, score))
        else:
            # Fallback: look for any number in first line
            first_line = response.split("\n")[0]
            numbers = re.findall(r"\d+", first_line)
            score = int(numbers[0]) if numbers else 7  # Default to 7 if no score found

        # Try to extract FEEDBACK: [text]
        feedback_match = re.search(
            r"FEEDBACK:\s*(.+)", response, re.IGNORECASE | re.DOTALL
        )
        if feedback_match:
            feedback = feedback_match.group(1).strip()
        else:
            # Fallback: use everything after first line
            lines = response.split("\n", 1)
            feedback = lines[1].strip() if len(lines) > 1 else response.strip()

        return score, feedback

    except Exception as e:
        print(f"Error parsing critique response: {e}")
        # Safe fallback
        return 7, response.strip()
