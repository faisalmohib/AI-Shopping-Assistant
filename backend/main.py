from fastapi import FastAPI
from routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routes.product import router as product_router
from routes.cart import router as cart_router
from routes.order import router as order_router
from routes.wishlist import router as wishlist_router
from routes.recent import router as recent_router
from routes.recommendation import router as rec_router
from routes.description import router as description_router
from routes.recommendDD import router as recommend_router
from routes.chatbot import router as chatbot_router




from agent import graph

from database import (
    get_product_by_id,
    get_product_sizes
)



app = FastAPI()

# Register routes
app.include_router(product_router)
app.include_router(auth_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(wishlist_router)
app.include_router(recent_router)
app.include_router(rec_router)
app.include_router(description_router)
app.include_router(recommend_router)
app.include_router(chatbot_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Backend Running"}


@app.post("/search")
def search_products(data: SearchRequest):

    output = graph.invoke(
        {"question": data.question}
    )

    products = []

    results = output["result"]

    if results and not isinstance(results[0], str):

        for row in results:

            products.append({
                "id": row[0],
                "product_id": row[1],
                "name": row[2],
                "price": row[3],
                "color": row[4],
                "brand": row[5],
                "image": row[6],
                "url": row[7],
                "target_audience": row[8],
                "category": row[9]
            })

    return {
        "route": output["route"],
        "sql": output["sql"],
        "products": products
    }

@app.get("/product/{product_id}")
def product_details(product_id: int):

    row = get_product_by_id(product_id)

    if not row:
        return {
            "success": False
        }

    return {
        "success": True,

        "product": {
            "id": row[0],
            "product_id": row[1],
            "name": row[2],
            "price": row[3],
            "color": row[4],
            "brand": row[5],
            "image": row[6],
            "url": row[7],
            "target_audience": row[8],
            "category": row[9]
        }
    }


@app.get("/product/{product_id}/sizes")
def product_sizes(product_id: int):

    product = get_product_by_id(product_id)

    if not product:
        return []

    shopify_product_id = product[1]

    rows = get_product_sizes(
        shopify_product_id
    )

    return [
        {
            "size": row[0],
            "available": row[1]
        }
        for row in rows
    ]