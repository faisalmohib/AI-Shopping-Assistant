import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from database import query_products

from prompts.router_prompt import ROUTER_PROMPT
from prompts.men_prompt import MEN_PROMPT
from prompts.women_prompt import WOMEN_PROMPT
from prompts.kids_girls_prompt import KIDS_GIRLS_PROMPT
from prompts.kids_boys_prompt import KIDS_BOYS_PROMPT

load_dotenv()

#llama-3.3-70b-versatile
llm = ChatGroq(
    model_name="openai/gpt-oss-20b",
    groq_api_key=os.getenv("GROQ_API_KEY")
)


class AgentState(TypedDict):
    question: str
    route: str
    sql: str
    result: list


def generate_sql(state: AgentState):

    question = state["question"]

    route_response = llm.invoke(
        ROUTER_PROMPT + "\n" + question
    )

    route = route_response.content.strip().upper()

    if route == "WOMEN":
        selected_prompt = WOMEN_PROMPT
    elif route == "MEN":
        selected_prompt = MEN_PROMPT
    elif route == "KIDS_BOYS":
        selected_prompt = KIDS_BOYS_PROMPT
    else:
        selected_prompt = KIDS_GIRLS_PROMPT
        

    sql_response = llm.invoke(
        selected_prompt +
        "\n\nQuestion: " +
        question
    )

    sql = sql_response.content.strip()

    return {
        "question": question,
        "route": route,
        "sql": sql
    }


def execute_sql(state: AgentState):

    try:
        rows = query_products(state["sql"])

        return {
            **state,
            "result": rows
        }

    except Exception as e:

        return {
            **state,
            "result": [f"SQL Error: {str(e)}"]
        }


builder = StateGraph(AgentState)

builder.add_node("generate_sql", generate_sql)
builder.add_node("execute_sql", execute_sql)

builder.set_entry_point("generate_sql")

builder.add_edge("generate_sql", "execute_sql")
builder.add_edge("execute_sql", END)

graph = builder.compile()