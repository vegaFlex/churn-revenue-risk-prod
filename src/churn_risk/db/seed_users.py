from __future__ import annotations

from sqlalchemy import select

from churn_risk.auth.service import hash_password
from churn_risk.config import settings
from churn_risk.db.base import SessionLocal
from churn_risk.db.models import AppUser


def build_seed_users() -> list[dict[str, str]]:
    users = [
        {"username": "viewer_demo", "password": "ViewerPass123!", "role": "viewer"},
    ]
    if settings.admin_username and settings.admin_password:
        users.append(
            {
                "username": settings.admin_username,
                "password": settings.admin_password,
                "role": "admin",
            }
        )
    return users


def main() -> None:
    seed_users = build_seed_users()
    with SessionLocal() as session:
        for user_data in seed_users:
            stmt = select(AppUser).where(AppUser.username == user_data["username"])
            existing = session.execute(stmt).scalar_one_or_none()
            if existing is None:
                session.add(
                    AppUser(
                        username=user_data["username"],
                        password_hash=hash_password(user_data["password"]),
                        role=user_data["role"],
                        is_active=1,
                    )
                )
        session.commit()

    seeded_roles = ", ".join(sorted({user["role"] for user in seed_users}))
    print(f"Users seeded successfully. Roles included: {seeded_roles}")


if __name__ == "__main__":
    main()
