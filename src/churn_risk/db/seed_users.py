from __future__ import annotations

from sqlalchemy import select

from churn_risk.auth.service import hash_password
from churn_risk.db.base import SessionLocal
from churn_risk.db.models import AppUser


DEMO_USERS = [
    {"username": "viewer_demo", "password": "ViewerPass123!", "role": "viewer"},
]


def main() -> None:
    with SessionLocal() as session:
        for user_data in DEMO_USERS:
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

    print("Demo users seeded successfully.")


if __name__ == "__main__":
    main()
