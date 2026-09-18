from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uuid

from rag_agent import graph


router = APIRouter()


# store conversations
threads = {}


class ChatRequest(BaseModel):
    user_id: int
    message: str



@router.post("/chat")
def chat(req: ChatRequest):

    try:

        # create memory thread for user
        if req.user_id not in threads:

            threads[req.user_id] = {
                "configurable": {
                    "thread_id": str(uuid.uuid4())
                }
            }


        config = threads[req.user_id]


        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=req.message
                    )
                ]
            },
            config=config
        )


        answer = ""


        # get final AI answer
        for msg in reversed(result["messages"]):

            if hasattr(msg, "content"):

                if hasattr(msg, "tool_calls"):

                    if not msg.tool_calls:

                        answer = msg.content
                        break

                else:

                    answer = msg.content
                    break



        if not answer:

            answer = "Sorry, I could not generate an answer."



        return {
            "answer": answer
        }



    except Exception as e:

        print("CHATBOT ERROR:", e)

        return {
            "answer": "Sorry, something went wrong."
        }