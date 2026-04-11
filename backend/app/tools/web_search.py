from ddgs import DDGS
from typing import List, Dict


def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)

    Returns:
        List of dicts with keys: title, url, snippet
    """
    try:
        ddgs = DDGS()
        results = []

        # DuckDuckGo text search
        search_results = ddgs.text(query, max_results=max_results)

        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
            })

        return results

    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return []


def deduplicate_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate results based on URL.

    Args:
        results: List of search result dicts

    Returns:
        Deduplicated list of results
    """
    seen_urls = set()
    unique_results = []

    for result in results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)

    return unique_results
