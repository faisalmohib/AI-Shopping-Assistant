
from fastapi import APIRouter
from recommendation.recommendation_service import get_similar_products

router = APIRouter()


@router.get("/recommend/{product_id}")
def recommend(product_id: int, top_k: int = 5):

    results = get_similar_products(product_id, top_k)

    return {
        "products": results
    }