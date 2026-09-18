from fastapi import APIRouter

from database import (
    get_recent_searches,
    get_recently_viewed_ids
)

from recommendation.recommendation_service import (
    get_similar_products,
    get_text_recommendations,
    get_hybrid_recommendations
)

router = APIRouter()


# =========================================================
# TEXT SEARCH ONLY (OPTIONAL DEBUG ENDPOINT)
# =========================================================
@router.get("/recommendations/text")
def text_recommend(q: str, k: int = 5):

    return get_text_recommendations(q, k)


# =========================================================
# PRODUCT SIMILARITY (OPTIONAL DEBUG ENDPOINT)
# =========================================================
@router.get("/recommendations/product/{product_id}")
def similar(product_id: int):

    return get_similar_products(product_id)


# =========================================================
# MAIN USER RECOMMENDATION ENGINE 🚀
# =========================================================
@router.get("/recommendations/{user_id}")
def user_recommendations(user_id: int):

    # ------------------
    # Collect user signals
    # ------------------

    searches = get_recent_searches(user_id)
    viewed = get_recently_viewed_ids(user_id)

    # ------------------
    # Build input for hybrid AI engine
    # ------------------

    return get_hybrid_recommendations(

        text=" ".join(searches),   # combine search history

        cart_items=[],             # optional (future DB integration)
        wishlist_items=[],
        order_items=[],

        history_items=viewed,

        top_k=8
    )