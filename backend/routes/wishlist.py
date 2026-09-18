from fastapi import APIRouter
from pydantic import BaseModel

from database import (
    add_to_wishlist,
    get_wishlist,
    remove_from_wishlist,
    clear_wishlist,
    add_to_cart
)

router = APIRouter()


class WishlistRequest(BaseModel):
    user_id: int
    product_id: int





@router.post("/wishlist/add")
def wishlist_add(data: WishlistRequest):

    success = add_to_wishlist(
        data.user_id,
        data.product_id
    )

    if not success:

        return {
            "success": False,
            "message": "Already in wishlist"
        }

    return {
        "success": True,
        "message": "Added to wishlist"
    }


@router.get("/wishlist/{user_id}")
def wishlist(user_id: int):

    rows = get_wishlist(user_id)

    products = []

    for row in rows:

        products.append({
            "wishlist_id": row[0],
            "product_id": row[1],
            "name": row[2],
            "price": row[3],
            "color": row[4],
            "brand": row[5],
            "image": row[6],
            "url": row[7]
        })

    return products


@router.delete("/wishlist/{wishlist_id}")
def delete_wishlist(wishlist_id: int):

    remove_from_wishlist(wishlist_id)

    return {
        "success": True
    }


@router.delete("/wishlist/clear/{user_id}")
def clear(user_id: int):

    clear_wishlist(user_id)

    return {
        "success": True
    }


