"""
seed.py — Populate the database with demo users and financial records.

Usage:
    python seed.py

Creates:
    - 1 Admin  : admin@demo.com    / admin123
    - 1 Analyst: analyst@demo.com  / analyst123
    - 1 Viewer : viewer@demo.com   / viewer123
    - 30 sample financial records
"""

import sys
import os
from datetime import date, timedelta
import random

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.financial_record import FinancialRecord, RecordType

Base.metadata.create_all(bind=engine)

CATEGORIES_INCOME = ["salary", "freelance", "investment", "rental", "bonus"]
CATEGORIES_EXPENSE = ["rent", "groceries", "utilities", "transport", "entertainment", "healthcare", "subscriptions"]

def seed():
    db = SessionLocal()

    # Clean slate
    db.query(FinancialRecord).delete()
    db.query(User).delete()
    db.commit()

    # ── Users ─────────────────────────────────────────────────────────────────
    admin = User(
        name="Admin User",
        email="admin@demo.com",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
    )
    analyst = User(
        name="Analyst User",
        email="analyst@demo.com",
        hashed_password=hash_password("analyst123"),
        role=UserRole.analyst,
    )
    viewer = User(
        name="Viewer User",
        email="viewer@demo.com",
        hashed_password=hash_password("viewer123"),
        role=UserRole.viewer,
    )
    db.add_all([admin, analyst, viewer])
    db.commit()
    db.refresh(admin)

    print("✓ Created users: admin@demo.com, analyst@demo.com, viewer@demo.com")

    # ── Financial Records ─────────────────────────────────────────────────────
    records = []
    today = date.today()

    for i in range(30):
        record_date = today - timedelta(days=random.randint(0, 180))
        is_income = random.choice([True, False])
        records.append(
            FinancialRecord(
                amount=round(random.uniform(10, 5000), 2),
                type=RecordType.income if is_income else RecordType.expense,
                category=random.choice(CATEGORIES_INCOME if is_income else CATEGORIES_EXPENSE),
                date=record_date,
                notes=f"Sample record #{i+1}",
                created_by=admin.id,
            )
        )

    db.add_all(records)
    db.commit()
    print(f"✓ Created {len(records)} financial records")
    print("\nSeed complete! You can now log in with:")
    print("  admin@demo.com    / admin123")
    print("  analyst@demo.com  / analyst123")
    print("  viewer@demo.com   / viewer123")

    db.close()


if __name__ == "__main__":
    seed()
