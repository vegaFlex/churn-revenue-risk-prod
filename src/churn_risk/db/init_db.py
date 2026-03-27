from __future__ import annotations

from churn_risk.db.base import Base, engine
from churn_risk.db import models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    main()
