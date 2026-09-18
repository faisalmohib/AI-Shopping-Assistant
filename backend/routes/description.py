import os
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_groq import ChatGroq

load_dotenv()

router = APIRouter()

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def safe_get(product, key, default=""):
    try:
        return product.get(key, default)
    except:
        return default


def generate_product_description(product):

    name = safe_get(product, "name")
    price = safe_get(product, "price")
    color = safe_get(product, "color")
    brand = safe_get(product, "brand")
    category = safe_get(product, "category")
    audience = safe_get(product, "target_audience")

    prompt = f"""
You are a world-class e-commerce copywriter.

Write a 2-3 line product description.

Rules:
- Simple English
- No emojis
- No exaggeration
- Focus on lifestyle and usability

Product:
Name: {name}
Price: {price}
Color: {color}
Brand: {brand}
Category: {category}
Audience: {audience}
"""

    response = llm.invoke(prompt)

    return response.content.strip()


@router.post("/product/description")
def product_description(payload: dict):

    product = payload.get("product")

    if not product:
        return {
            "description": "No product provided."
        }

    description = generate_product_description(product)

    return {
        "description": description
    }