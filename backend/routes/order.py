from fastapi import APIRouter
from pydantic import BaseModel

from database import (
    create_cart_order,
    create_direct_order,
    get_user_orders,
    get_order_items,
    get_payment_profile,
    save_payment_profile
)

router = APIRouter()

# =========================================================
# CHECKOUT REQUEST (Cart + Buy Now)
# =========================================================

class CheckoutRequest(BaseModel):
    user_id: int
    customer_name: str
    phone: str
    address: str

    payment_method: str
    card_number: str = ""
    expiry: str = ""
    cvv: str = ""

    # Buy Now optional
    product_id: int | None = None
    product_name: str = ""
    price: float = 0.0
    quantity: int = 1


@router.post("/checkout")
def checkout(data: CheckoutRequest):

    # -------------------------
    # VALIDATION
    # -------------------------
    if not data.phone:
        return {"success": False, "message": "Phone is required"}

    if not data.address:
        return {"success": False, "message": "Address is required"}

    if data.payment_method == "Card":

        if not data.card_number:
            return {"success": False, "message": "Card number required"}

        if not data.expiry:
            return {"success": False, "message": "Expiry required"}

        if not data.cvv:
            return {"success": False, "message": "CVV required"}

    # -------------------------
    # BUY NOW FLOW
    # -------------------------
    if data.product_id:

        order_id = create_direct_order(
            user_id=data.user_id,
            product_id=data.product_id,
            product_name=data.product_name,
            price=data.price,
            customer_name=data.customer_name,
            phone=data.phone,
            address=data.address,
            quantity=data.quantity
        )

    # -------------------------
    # CART FLOW
    # -------------------------
    else:

        order_id = create_cart_order(
            user_id=data.user_id,
            customer_name=data.customer_name,
            phone=data.phone,
            address=data.address
        )

    if not order_id:
        return {"success": False, "message": "Unable to place order"}

    return {
        "success": True,
        "order_id": order_id
    }


# =========================================================
# AI DIRECT BUY SYSTEM 🤖
# =========================================================

class DirectBuyRequest(BaseModel):
    user_id: int
    product_id: int
    product_name: str
    price: float
    quantity: int = 1

    # first-time fallback
    customer_name: str = ""
    phone: str = ""
    address: str = ""

    # payment (first time only)
    card_number: str = ""
    expiry: str = ""
    cvv: str = ""


@router.post("/direct-buy")
def direct_buy(data: DirectBuyRequest):

    # 1. Get saved profile
    profile = get_payment_profile(data.user_id)

    # 2. FIRST TIME USER
    if not profile:

        if not data.phone or not data.address:
            return {
                "success": False,
                "message": "Profile not found. Please provide address & payment details."
            }

        save_payment_profile(
            user_id=data.user_id,
            phone=data.phone,
            address=data.address,
            card_number=data.card_number,
            expiry=data.expiry,
            cvv=data.cvv
        )

        phone = data.phone
        address = data.address

    # 3. RETURNING USER
    else:
        phone = profile["phone"]
        address = profile["address"]

    # 4. CREATE ORDER (FIXED)
    order_id = create_direct_order(
        user_id=data.user_id,
        product_id=data.product_id,
        product_name=data.product_name,
        price=data.price,
        customer_name=data.customer_name or "AI User",
        phone=phone,
        address=address,
        quantity=data.quantity
    )

    return {
        "success": True,
        "message": "Order placed successfully via AI Direct Buy",
        "order_id": order_id
    }


# =========================================================
# ORDER HISTORY
# =========================================================

@router.get("/orders/{user_id}")
def user_orders(user_id: int):

    rows = get_user_orders(user_id)

    return [
        {
            "id": r[0],
            "total_amount": r[1],
            "created_at": r[2]
        }
        for r in rows
    ]


@router.get("/order/{order_id}")
def order_details(order_id: int):

    items = get_order_items(order_id)

    return {
        "items": [
            {
                "product_name": i[0],
                "quantity": i[1],
                "price": i[2]
            }
            for i in items
        ]
    }