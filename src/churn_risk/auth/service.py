from __future__ import annotations

from collections.abc import Callable
from typing import Any

import bcrypt
from fastapi import HTTPException, Request, status
from sqlalchemy import select

from churn_risk.db.base import SessionLocal
from churn_risk.db.models import AppUser


ROLE_ORDER = {
    "viewer": 1,
    "analyst": 2,
    "admin": 3,
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    with SessionLocal() as session:
        stmt = select(AppUser).where(AppUser.username == username, AppUser.is_active == 1)
        user = session.execute(stmt).scalar_one_or_none()

    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None

    return {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
    }


def get_current_user(request: Request) -> dict[str, Any] | None:
    return request.session.get("user")


def require_role(minimum_role: str) -> Callable[[Request], dict[str, Any]]:
    def dependency(request: Request) -> dict[str, Any]:
        user = get_current_user(request)
        if user is None:
            raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail="Authentication required")

        current_rank = ROLE_ORDER.get(user["role"], 0)
        required_rank = ROLE_ORDER.get(minimum_role, 0)
        if current_rank < required_rank:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

        return user

    return dependency
