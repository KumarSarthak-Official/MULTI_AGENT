from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings
import os


class LLMService:
    """Wrapper for Ollama Cloud LLM interactions."""

    def __init__(self):
        # Set API key as environment variable for langchain-ollama
        os.environ["OLLAMA_API_KEY"] = settings.OLLAMA_API_KEY

        self.llm = ChatOllama(
            model=settings.LLM_MODEL,
            base_url=settings.OLLAMA_CLOUD_URL,
            temperature=0.7,
        )

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text from a prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context

        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = self.llm.invoke(messages)
        return response.content

    def generate_queries(self, topic: str, num_queries: int = 3) -> list[str]:
        """Generate diverse search queries for a research topic.

        Args:
            topic: Research topic
            num_queries: Number of queries to generate (default 3)

        Returns:
            List of search query strings
        """
        system_prompt = """You are a research assistant that generates diverse search queries.
Given a research topic, generate multiple search queries that explore different aspects and perspectives.
Each query should be specific and actionable for web search."""

        prompt = f"""Generate {num_queries} diverse search queries for researching this topic:
Topic: {topic}

Return ONLY the queries, one per line, without numbering or explanation."""

        response = self.generate(prompt, system_prompt)
        queries = [q.strip() for q in response.strip().split("\n") if q.strip()]
        return queries[:num_queries]


# Singleton instance
llm_service = LLMService()
