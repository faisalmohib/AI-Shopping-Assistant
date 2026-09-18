from fastapi import APIRouter

from database import get_product

router = APIRouter()


@router.get("/product/{product_id}")
def product_details(product_id: int):

    row = get_product(product_id)

    if not row:
        return {}

    return {
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