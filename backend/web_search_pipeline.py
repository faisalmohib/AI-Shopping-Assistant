# web_search_pipeline.py
# Standalone internet/product search module.
# Designed to later be wrapped as a LangGraph tool (e.g. via @tool) and
# combined with rag_pipeline.py's RAGRetriever as a second tool, with an
# LLM/router deciding which one to call.

import os
import json
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv()

from tavily import TavilyClient
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


class WebSearchManager:
    """Handles internet search via the Tavily API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key is required. Set TAVILY_API_KEY in your .env "
                "or pass api_key directly."
            )
        self.client = TavilyClient(api_key=self.api_key)

    def search(
        self,
        query: str,
        max_results: int = 10,
        score_threshold: float = 0.3,
        include_domains: Optional[List[str]] = None,
        topic: str = "general",
    ) -> List[Dict[str, Any]]:
        """
        Search the web for a query.

        Args:
            query: search query (e.g. "J. Junaid Jamshed lawn collection 2026 price")
            max_results: max candidates to pull from Tavily before relevance filtering
            score_threshold: minimum relevance score (0-1) a result must have to be kept.
                              This is what actually controls how many results come back -
                              not a fixed count - so the number returned varies with how
                              many results are genuinely relevant to the query.
            include_domains: optional list of domains to restrict search to
                              (e.g. ["junaidjamshed.com"] to search only the brand's own site)
            topic: "general" or "news" (Tavily-supported topics)

        Returns:
            List of dicts: {title, url, content, score}
        """
        print(f"Searching the web for: '{query}'")
        try:
            kwargs = {
                "query": query,
                "max_results": max_results,
                "topic": topic,
            }
            if include_domains:
                kwargs["include_domains"] = include_domains

            response = self.client.search(**kwargs)
            results = []
            for r in response.get("results", []):
                score = r.get("score", 0.0)
                if score < score_threshold:
                    continue
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "score": score,
                    }
                )
            print(f"Found {len(results)} web results above score_threshold={score_threshold}")
            return results

        except Exception as e:
            print(f"Error during web search: {e}")
            return []


class QueryPlanner:
    """
    Detects when a query asks about multiple distinct brands/entities
    (e.g. "price on Gul Ahmad and Khaddi") and splits it into separate
    per-entity search queries, so each entity gets its own dedicated
    search instead of one combined query that can get dominated by
    whichever brand has stronger SEO presence.
    """

    def __init__(self, model_name: str = "openai/gpt-oss-20b", api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")
        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=model_name,
            temperature=0.0,
            max_tokens=300,
        )

    def split(self, query: str) -> List[str]:
        """
        Returns a list of search queries. If the question only concerns one
        entity/topic, returns a single-item list with the original query
        unchanged. If it compares/asks about multiple distinct brands or
        entities, returns one focused query per entity.
        """
        system_prompt = """You turn a user's question into one or more focused web search
queries. Rules:

1. If the question mentions multiple distinct brands, stores, or products being compared or
   asked about together (e.g. "X and Y", "X vs Y"), output ONE search query per entity, each
   keeping the same attribute being asked about (price, availability, etc.).
2. If the question only concerns a single brand/entity/topic, output exactly one search query:
   the question itself, lightly cleaned up for search if needed.
3. If a brand name is short or could be confused with a generic/dictionary word or a different
   brand (e.g. "Khaddi" vs "Khadi", "J." vs a generic letter), add disambiguating context to that
   query, such as the country, "clothing brand", or the likely official domain name, so the search
   doesn't return results for the wrong entity. When in doubt, add disambiguating words rather than
   risk an ambiguous query.
4. Output ONLY a JSON array of strings, nothing else. No explanation, no markdown formatting.

Example input: "what is price of cotton for men on gul ahmad and khaddi"
Example output: ["Gul Ahmad cotton fabric for men price", "Khaddi clothing brand Pakistan cotton fabric for men price"]

Example input: "does khaddi have lawn suits"
Example output: ["Khaddi clothing brand Pakistan lawn suits"]"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query),
            ]
            response = self.llm.invoke(messages)
            raw = response.content.strip()
            # Strip accidental code fences
            raw = raw.replace("```json", "").replace("```", "").strip()
            # Sometimes the model wraps in extra text — try to extract just the array
            if "[" in raw and "]" in raw:
                raw = raw[raw.index("["):raw.rindex("]") + 1]
            subqueries = json.loads(raw)
            if isinstance(subqueries, list) and all(isinstance(q, str) for q in subqueries) and subqueries:
                return subqueries
        except Exception as e:
            print(f"QueryPlanner fallback (couldn't split query): {e}")

        return [query]


def multi_search(
    query: str,
    search_manager: WebSearchManager,
    planner: QueryPlanner,
    score_threshold: float = 0.3,
    include_domains: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Splits the query into per-entity sub-queries (if needed), runs a separate
    search for each, and merges the results (deduplicated by URL). Result count
    is governed by score_threshold, not a fixed number - so it naturally varies
    per query instead of always returning the same count.
    """
    subqueries = planner.split(query)
    if len(subqueries) > 1:
        print(f"Query split into {len(subqueries)} sub-searches: {subqueries}")

    merged_results: List[Dict[str, Any]] = []
    seen_urls = set()
    for sq in subqueries:
        results = search_manager.search(sq, score_threshold=score_threshold, include_domains=include_domains)
        for r in results:
            url = r.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged_results.append(r)

    return merged_results


class ProductSearchLLM:
    """Synthesizes a grounded answer from web search results using Groq."""

    def __init__(self, model_name: str = "openai/gpt-oss-20b", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")

        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model_name,
            temperature=0.1,
            max_tokens=1024,
        )
        print(f"Initialized ProductSearchLLM with model: {self.model_name}")

    def generate_response(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Generate a grounded answer from web search results, with source citations.

        Args:
            query: the user's question
            search_results: list of dicts from WebSearchManager.search()

        Returns:
            Generated answer string
        """
        if not search_results:
            return "I couldn't find any relevant information online for that."

        # Plain context block (no [n] markers) - the LLM just writes a direct answer.
        context_blocks = []
        for r in search_results:
            context_blocks.append(f"Title: {r['title']}\nContent: {r['content']}")
        context = "\n\n".join(context_blocks)

        system_prompt = """You are a product research assistant. Answer ONLY using the web
content provided below, tailored directly to the user's question. Follow these rules strictly:

1. Do not use outside knowledge.
2. Extract and state every specific, relevant fact you can find (prices, product names, sizes, etc.),
   even if it only partially answers the question. Do not refuse to answer just because some part of
   the question isn't covered - answer the part you can, and explicitly say which part is missing.
   Example: if asked about prices for "X and Y" but the content only covers X, give the X prices and
   say "I couldn't find pricing for Y in these results" - do not say "I don't have that information"
   for the whole question.
3. If multiple different prices/products appear, list them out rather than picking one silently.
4. Only say you have no relevant information if NONE of the content relates to the question at all.
5. Give a direct, concise answer to exactly what was asked. No preamble, no citation markers, no source list -
   just the answer itself."""

        user_prompt = f"""Web content:
{context}

Question: {query}

Answer using only the rules above."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"


def search_products(query: str, score_threshold: float = 0.3, include_domains: Optional[List[str]] = None) -> str:
    """
    Convenience function: search the web (splitting multi-entity questions into
    separate searches when needed) and return a synthesized, grounded answer.
    This is the function signature you'll likely wrap with @tool for LangGraph later.
    """
    search_manager = WebSearchManager()
    planner = QueryPlanner()
    llm = ProductSearchLLM()
    results = multi_search(query, search_manager, planner, score_threshold=score_threshold, include_domains=include_domains)
    return llm.generate_response(query, results)


class SearchSession:
    """
    Tracks conversation state across turns so follow-ups like "show me more"
    or "any other options" return NEW results instead of repeating the same
    ones, without needing to re-query Tavily for the same search term (which
    would just return the same ranked results again).

    How it works:
    - On a fresh topic, it pulls a larger pool of candidate results up front
      and shows the first batch.
    - On a follow-up ("more", "other options", "anything else"), it serves
      the next batch from the already-fetched pool.
    - If the pool runs out, it does one more search (excluding URLs already
      shown) to top up the pool before serving the next batch.
    """

    FOLLOWUP_PHRASES = (
        "more", "any more", "show more", "other options", "any other",
        "anything else", "else", "different", "another", "more options",
        "more suits", "more results", "what else",
    )

    def __init__(
        self,
        search_manager: Optional[WebSearchManager] = None,
        planner: Optional[QueryPlanner] = None,
        llm: Optional[ProductSearchLLM] = None,
        batch_size: int = 5,
        pool_fetch_score_threshold: float = 0.2,
    ):
        self.search_manager = search_manager or WebSearchManager()
        self.planner = planner or QueryPlanner()
        self.llm = llm or ProductSearchLLM()
        self.batch_size = batch_size
        self.pool_fetch_score_threshold = pool_fetch_score_threshold

        self.last_topic: Optional[str] = None
        self.result_pool: List[Dict[str, Any]] = []
        self.shown_count: int = 0
        self.include_domains: Optional[List[str]] = None

    def _is_followup(self, message: str) -> bool:
        if not self.last_topic:
            return False
        msg = message.lower().strip()
        # short messages matching a known follow-up phrase, OR the message
        # is just "more" plus a generic noun from the original topic
        return any(phrase in msg for phrase in self.FOLLOWUP_PHRASES) and len(msg.split()) <= 6

    def _fetch_more(self, topic_query: str, include_domains: Optional[List[str]]):
        """Search again for the topic, only adding genuinely new URLs to the pool."""
        results = multi_search(
            topic_query,
            self.search_manager,
            self.planner,
            score_threshold=self.pool_fetch_score_threshold,
            include_domains=include_domains,
        )
        existing_urls = {r["url"] for r in self.result_pool}
        new_results = [r for r in results if r.get("url") not in existing_urls]
        self.result_pool.extend(new_results)
        return len(new_results)

    def ask(self, message: str, include_domains: Optional[List[str]] = None) -> str:
        """
        Main entry point for a conversation turn. Pass the user's raw message;
        returns the bot's answer text.
        """
        is_followup = self._is_followup(message)

        if not is_followup:
            # New topic: reset session state
            self.last_topic = message
            self.result_pool = []
            self.shown_count = 0
            self.include_domains = include_domains
            self._fetch_more(self.last_topic, self.include_domains)

        # Serve next batch from the pool
        remaining = self.result_pool[self.shown_count:]
        if not remaining:
            # Pool exhausted - try one more fetch before giving up
            added = self._fetch_more(self.last_topic, self.include_domains)
            remaining = self.result_pool[self.shown_count:]
            if added == 0 or not remaining:
                return "I don't have any more results for that - that's everything I could find."

        batch = remaining[: self.batch_size]
        self.shown_count += len(batch)

        return self.llm.generate_response(self.last_topic, batch)


if __name__ == "__main__":
    # Quick manual test when running this file directly - demonstrates follow-up pagination
    session = SearchSession()
    print(session.ask("J. Junaid Jamshed lawn collection 2026 prices"))
    print("\n--- asking for more ---\n")
    print(session.ask("show me more"))