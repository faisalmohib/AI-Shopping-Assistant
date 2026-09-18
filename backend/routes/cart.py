from fastapi import APIRouter
from pydantic import BaseModel


from database import (
    add_to_cart,
    get_cart_items,
    remove_from_cart,
    clear_cart,
    get_cart_total
)

router = APIRouter()


class CartRequest(BaseModel):
    user_id: int
    product_id: int
    size: str
    quantity: int = 1


@router.post("/cart/add")
def add_cart(data: CartRequest):

    add_to_cart(
        user_id=data.user_id,
        product_id=data.product_id,
        size=data.size,
        quantity=data.quantity
    )

    return {
        "success": True,
        "message": "Added to cart"
    }

@router.get("/cart/{user_id}")
def get_cart(user_id: int):

    rows = get_cart_items(user_id)

    products = []

    for row in rows:

        products.append({
            "cart_id": row[0],
            "product_id": row[1],
            "name": row[2],
            "price": row[3],
            "image": row[4],
            "color": row[5],
            "brand": row[6],
            "quantity": row[7],
            "size": row[8]
        })

    return {
        "items": products,
        "total": get_cart_total(user_id)
    }


@router.delete("/cart/remove/{cart_id}")
def remove_item(cart_id: int):

    remove_from_cart(cart_id)

    return {
        "success": True
    }


@router.delete("/cart/clear/{user_id}")
def clear_user_cart(user_id: int):

    clear_cart(user_id)

    return {
        "success": True
    }