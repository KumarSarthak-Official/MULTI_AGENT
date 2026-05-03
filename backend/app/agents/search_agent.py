from app.agents.state import ResearchState
from app.services.llm_service import llm_service
from app.tools.web_search import search_web, deduplicate_results
from typing import Dict, Any


def search_agent_node(state: ResearchState) -> Dict[str, Any]:
    """Search Agent: Generates diverse queries and searches the web.

    Process:
    1. Generate 2 diverse search queries from the original topic
    2. Execute DuckDuckGo search for each query (max 4 results each)
    3. Deduplicate results by URL
    4. Return max 10 unique results

    Args:
        state: Current ResearchState

    Returns:
        Dict with updated search_results and agent_logs
    """
    query = state["query"]
    agent_logs = [f"Search Agent: Starting web search for '{query}'"]

    try:
        # Step 1: Generate diverse queries
        queries = llm_service.generate_queries(query, num_queries=2)
        agent_logs.append(f"Search Agent: Generated {len(queries)} search queries")

        # Step 2: Search for each query
        all_results = []
        for q in queries:
            results = search_web(q, max_results=4)
            all_results.extend(results)
            agent_logs.append(f"Search Agent: Found {len(results)} results for '{q}'")

        # Step 3: Deduplicate by URL
        unique_results = deduplicate_results(all_results)
        agent_logs.append(
            f"Search Agent: Deduplicated to {len(unique_results)} unique results"
        )

        # Step 4: Limit to max 10 results
        final_results = unique_results[:10]
        agent_logs.append(
            f"Search Agent: Returning {len(final_results)} search results"
        )

        return {
            "search_results": final_results,
            "agent_logs": agent_logs,
        }

    except Exception as e:
        error_msg = f"Search Agent: Error - {str(e)}"
        agent_logs.append(error_msg)
        return {
            "search_results": [],
            "agent_logs": agent_logs,
            "error": error_msg,
        }
