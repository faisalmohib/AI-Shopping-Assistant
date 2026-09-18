from fastapi import APIRouter

from pydantic import BaseModel

from database import (
    add_recently_viewed,
    get_recently_viewed,
    save_search_query,
    get_search_history
)

router = APIRouter()


class RecentlyViewedRequest(BaseModel):
    user_id: int
    product_id: int


class SearchHistoryRequest(BaseModel):
    user_id: int
    query: str


# ==========================
# Recently Viewed
# ==========================

@router.post("/recently-viewed/add")
def save_recent(data: RecentlyViewedRequest):

    add_recently_viewed(
        data.user_id,
        data.product_id
    )

    return {
        "success": True
    }


@router.get("/recently-viewed/{user_id}")
def recent_products(user_id: int):

    rows = get_recently_viewed(user_id)

    products = []

    for row in rows:

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

    return products


# ==========================
# Search History
# ==========================

@router.post("/search/history")
def save_history(data: SearchHistoryRequest):

    save_search_query(
        data.user_id,
        data.query
    )

    return {
        "success": True
    }


@router.get("/search/history/{user_id}")
def search_history(user_id: int):

    rows = get_search_history(user_id)

    history = []

    for row in rows:

        history.append({
            "query": row[0],
            "created_at": row[1]
        })

    return history