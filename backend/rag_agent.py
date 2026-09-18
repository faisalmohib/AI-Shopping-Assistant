
import os
from typing import Annotated
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from typing_extensions import TypedDict

# Import your existing pipeline components.
# Importing rag_pipeline connects to the existing persisted ChromaDB collection
# at data/vector_store — no re-indexing happens.
from rag_pipeline import rag_retriever
from web_search_pipeline import WebSearchManager, QueryPlanner, multi_search


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    # add_messages is a LangGraph reducer that appends new messages rather
    # than overwriting — this gives us the full conversation history for free.
    messages: Annotated[list, add_messages]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def search_knowledge_base(query: str) -> str:
    """Search the J. Junaid Jamshed internal knowledge base but in giving answer dont mention jdot.
    Use this for any question about company policies, return and exchange
    rules, shipping and delivery, payment methods, vouchers, contact info,
    about the company, or the fabric glossary which we sell.
    Input: a concise search query (not the user's raw message).
    """
    results = rag_retriever.retrieve(query, top_k=8, score_threshold=0.1)
    if not results:
        return "No relevant information found in the knowledge base for that query."
    return "\n\n---\n\n".join(r["content"] for r in results)


@tool
def search_web_for_products(query: str) -> str:
    """Search the internet for current product information, prices, availability,
    and comparisons across fashion brands (e.g. Gul Ahmad, Khaddi, J., etc.).
    Use this for any product-related question that needs up-to-date prices or
    external brand info (and also bring the links of items if searched on web), not covered by the internal knowledge base.
    Input: a concise, brand-aware search query.
    """
    search_manager = WebSearchManager()
    planner = QueryPlanner()
    results = multi_search(query, search_manager, planner, score_threshold=0.2)
    if not results:
        return "No relevant web results found for that query."
    # Return structured context so the responder can synthesize a clean answer.
    blocks = []
    for r in results:
        blocks.append(f"Source: {r['url']}\nTitle: {r['title']}\nContent: {r['content']}")
    return "\n\n---\n\n".join(blocks)


TOOLS = [search_knowledge_base, search_web_for_products]


# ---------------------------------------------------------------------------
# LLMs
# ---------------------------------------------------------------------------

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Set it in your .env file.")


router_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=0.0,
    max_tokens=512,
).bind_tools(TOOLS)

# Responder: fast model — just synthesizes a clean answer from tool output.
responder_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-20b",
    temperature=0.1,
    max_tokens=1024,
)

ROUTER_SYSTEM = """
You are an intelligent routing assistant for a customer support chatbot.

Your job is ONLY to decide whether to:
1. Answer directly (for greetings or simple conversation),
2. Call the internal knowledge base,
3. Call the web search tool.

You have two tools:

1. search_knowledge_base
Use this ONLY for questions about the company's internal information, including:
- Return policy
- Exchange policy
- Refund policy
- Shipping & Delivery
- Payment methods
- Order cancellation
- Order tracking
- Voucher & Discount policy
- Terms & Conditions
- Privacy Policy
- Contact information
- Store locations
- About the company
- Fabric glossary
- Size guide
- Care instructions
- FAQs

2. search_web_for_products
Use this for ANY question related to products or information that changes over time, including:
- Product prices
- Product availability
- Product links
- New arrivals
- Sale items
- Collections
- Comparisons between brands
- Product recommendations
- Product reviews
- Best-selling products
- Khaddi products
- Gul Ahmed products
- Sapphire products
- Limelight products
- Ethnic products
- Any brand other than this company
- Anything requiring current internet information

Rules:

1. If the user asks about company policies or company information, ALWAYS use search_knowledge_base.

2. If the user asks about products, prices, availability, collections, comparisons, recommendations, or shopping, ALWAYS use search_web_for_products.

3. If the user mentions another clothing brand such as:
- Khaddi
- Gul Ahmed
- Sapphire
- Limelight
- Ethnic
- Bonanza
- Outfitters
- Breakout
or any other brand,
ALWAYS use search_web_for_products.

4. If the user asks for:
- product links
- URLs
- latest products
- newest arrivals
- current prices
- discounted items
- products under a budget
ALWAYS use search_web_for_products.

5. If the user asks:
"show more"
"more"
"next"
"similar"
"other options"
continue using the SAME tool that produced the previous answer.

6. Generate a clean search query for the selected tool instead of passing the user's entire message.

Examples:

User:
"What is your return policy?"

→ search_knowledge_base

User:
"What payment methods are accepted?"

→ search_knowledge_base

User:
"What is cambric fabric?"

→ search_knowledge_base

User:
"Show me 10 lawn suits."

→ search_web_for_products

User:
"Show Khaddi unstitched lawn."

→ search_web_for_products

User:
"Compare Gul Ahmed and Sapphire lawn."

→ search_web_for_products

User:
"Show dresses under 5000."

→ search_web_for_products

User:
"Give me product links."

→ search_web_for_products

User:
"Hello"

→ No tool.
Respond directly.

Never answer product questions yourself.
Always use the appropriate tool.
"""

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------


RESPONDER_SYSTEM = """
You are a customer support assistant.

Your ONLY job is to generate the final answer using the tool results.

Rules:

1. Use ONLY the information returned by the tools.

2. Never use your own knowledge.

3. Never invent prices, products, policies, URLs, or availability.

4. If the tool returned product information:
   - Present products clearly.
   - Include prices if available.
   - Include links if available.
   - Include availability if available.

5. If the tool returned policy information:
   - Answer only using that information.
   - Do not mix policies together.
   - Mention exceptions if they exist.

6. Match the user's requested format.
If they asked for:
- a list
- a table
- 10 products
- links
- comparisons

then answer in that format.

7. If the tool returned only partial information, clearly state what was found.

8. If no relevant information was returned, politely say you could not find relevant information.

9. Never mention internal implementation, vector databases, embeddings, retrieval, or tools.

10. At the end of every answer include:

Source: Knowledge Base

or

Source: Web Search

depending on which tool produced the information.

11. Be concise, factual, and professional.

Do not use any outside knowledge.
Only use the supplied tool results.
"""

def router_node(state: AgentState) -> dict:
    """
    Reads the conversation history from state and invokes the router LLM.
    We strip raw ToolMessages and tool-call AIMessages from history before
    sending to the router — it only needs the human/assistant conversation
    turns, not the full retrieved content, which prevents token bloat.
    """
    conversation_only = [
        msg for msg in state["messages"]
        if isinstance(msg, HumanMessage)
        or (isinstance(msg, AIMessage) and not msg.tool_calls)
    ]
    messages = [SystemMessage(content=ROUTER_SYSTEM)] + conversation_only
    response = router_llm.invoke(messages)
    return {"messages": [response]}


def responder_node(state: AgentState) -> dict:
    """
    Takes tool results from the most recent tool call and synthesizes a
    clean, grounded final answer for the user.
    """
    # Collect tool results from the end of the message list (most recent turn).
    tool_contents = []
    for msg in reversed(state["messages"]):
        if isinstance(msg, ToolMessage):
            tool_contents.append(msg.content)
        elif isinstance(msg, AIMessage) and msg.tool_calls:
            # Reached the AI message that triggered these tool calls — stop.
            break

    if not tool_contents:
        # Router gave a direct answer (no tool was called) — nothing to do.
        return {}

    context = "\n\n===\n\n".join(reversed(tool_contents))

    # Find the user's original question for this turn.
    user_question = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_question = msg.content
            break

    user_prompt = f"""Tool results:
{context}

User question: {user_question}

Answer:"""

    response = responder_llm.invoke([
        SystemMessage(content=RESPONDER_SYSTEM),
        HumanMessage(content=user_prompt),
    ])
    return {"messages": [AIMessage(content=response.content)]}


def should_continue(state: AgentState) -> str:
    """Route to tools if the router made a tool call, otherwise go straight to responder."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "responder"


# ---------------------------------------------------------------------------
# Graph
# ---------------------------------------------------------------------------

tool_node = ToolNode(TOOLS)

builder = StateGraph(AgentState)
builder.add_node("router", router_node)
builder.add_node("tools", tool_node)
builder.add_node("responder", responder_node)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", should_continue, {
    "tools": "tools",
    "responder": "responder",
})
builder.add_edge("tools", "responder")
builder.add_edge("responder", END)

# MemorySaver keeps conversation history in memory per thread_id.
# For persistence across Python restarts, swap this for SqliteSaver or
# PostgresSaver later.
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
with open("graph.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())

print("LangGraph agent compiled successfully.")