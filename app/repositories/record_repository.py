from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord, RecordType


class FinancialRecordRepository:
    """
    Handles all database interactions for FinancialRecord.
    Filtering, pagination, and aggregation queries live here.
    """

    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        """All queries exclude soft-deleted records by default."""
        return self.db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)  # noqa: E712

    def get_by_id(self, record_id: int) -> Optional[FinancialRecord]:
        return self._base_query().filter(FinancialRecord.id == record_id).first()

    def get_filtered(
        self,
        type: Optional[RecordType] = None,
        category: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[FinancialRecord], int]:
        """Returns (records, total_count) for the given filters."""
        query = self._base_query()

        if type:
            query = query.filter(FinancialRecord.type == type)
        if category:
            query = query.filter(FinancialRecord.category == category.lower())
        if date_from:
            query = query.filter(FinancialRecord.date >= date_from)
        if date_to:
            query = query.filter(FinancialRecord.date <= date_to)

        total = query.count()
        records = query.order_by(FinancialRecord.date.desc()).offset(skip).limit(limit).all()
        return records, total

    def create(
        self,
        amount: float,
        type: RecordType,
        category: str,
        date: date,
        created_by: int,
        notes: Optional[str] = None,
    ) -> FinancialRecord:
        record = FinancialRecord(
            amount=amount,
            type=type,
            category=category,
            date=date,
            notes=notes,
            created_by=created_by,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: FinancialRecord, **kwargs) -> FinancialRecord:
        for field, value in kwargs.items():
            if value is not None and hasattr(record, field):
                setattr(record, field, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def soft_delete(self, record: FinancialRecord) -> None:
        """Mark a record as deleted without removing it from the database."""
        record.is_deleted = True
        self.db.commit()

    # ── Aggregation queries for the dashboard ────────────────────────────────

    def get_total_by_type(self, record_type: RecordType) -> float:
        result = (
            self._base_query()
            .filter(FinancialRecord.type == record_type)
            .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0))
            .scalar()
        )
        return float(result)

    def get_totals_by_category(self, record_type: RecordType) -> list[dict]:
        rows = (
            self._base_query()
            .filter(FinancialRecord.type == record_type)
            .with_entities(
                FinancialRecord.category,
                func.sum(FinancialRecord.amount).label("total"),
            )
            .group_by(FinancialRecord.category)
            .order_by(func.sum(FinancialRecord.amount).desc())
            .all()
        )
        return [{"category": r.category, "total": float(r.total)} for r in rows]

    def get_monthly_trends(self) -> list[dict]:
        """Returns income and expense totals grouped by year and month."""
        rows = (
            self._base_query()
            .with_entities(
                func.extract("year", FinancialRecord.date).label("year"),
                func.extract("month", FinancialRecord.date).label("month"),
                FinancialRecord.type,
                func.sum(FinancialRecord.amount).label("total"),
            )
            .group_by("year", "month", FinancialRecord.type)
            .order_by("year", "month")
            .all()
        )

        # Merge income and expense rows into a single dict per month
        trends: dict[tuple, dict] = {}
        for row in rows:
            key = (int(row.year), int(row.month))
            if key not in trends:
                trends[key] = {"year": key[0], "month": key[1], "income": 0.0, "expense": 0.0}
            trends[key][row.type.value] += float(row.total)

        result = []
        for entry in trends.values():
            entry["net"] = entry["income"] - entry["expense"]
            result.append(entry)
        return result

    def get_recent(self, limit: int = 10) -> list[FinancialRecord]:
        return self._base_query().order_by(FinancialRecord.created_at.desc()).limit(limit).all()

    def get_total_count(self) -> int:
        return self._base_query().count()
