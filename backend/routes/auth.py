from fastapi import APIRouter
from pydantic import BaseModel

from services.auth_service import (
    register_user,
    login_user
)

router = APIRouter()


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: RegisterRequest):

    success, message = register_user(
        data.full_name,
        data.email,
        data.password
    )

    return {
        "success": success,
        "message": message
    }


@router.post("/login")
def login(data: LoginRequest):

    user = login_user(
        data.email,
        data.password
    )

    if user:

        return {
            "success": True,
            "user": user
        }

    return {
        "success": False,
        "message": "Invalid email or password"
    }