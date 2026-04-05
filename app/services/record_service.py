from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord
from app.models.user import User
from app.repositories.record_repository import FinancialRecordRepository
from app.schemas.financial_record import (
    PaginatedRecordsResponse,
    RecordCreateRequest,
    RecordFilterParams,
    RecordResponse,
    RecordUpdateRequest,
)


class FinancialRecordService:
    """
    Handles CRUD and filtering for financial records.
    Enforces business rules (e.g. only the creator or admin can delete).
    """

    def __init__(self, db: Session):
        self.repo = FinancialRecordRepository(db)

    def create_record(self, data: RecordCreateRequest, current_user: User) -> RecordResponse:
        record = self.repo.create(
            amount=data.amount,
            type=data.type,
            category=data.category,
            date=data.date,
            notes=data.notes,
            created_by=current_user.id,
        )
        return RecordResponse.model_validate(record)

    def get_records(self, filters: RecordFilterParams) -> PaginatedRecordsResponse:
        skip = (filters.page - 1) * filters.page_size
        records, total = self.repo.get_filtered(
            type=filters.type,
            category=filters.category,
            date_from=filters.date_from,
            date_to=filters.date_to,
            skip=skip,
            limit=filters.page_size,
        )
        return PaginatedRecordsResponse(
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            data=[RecordResponse.model_validate(r) for r in records],
        )

    def get_record(self, record_id: int) -> RecordResponse:
        record = self._get_or_404(record_id)
        return RecordResponse.model_validate(record)

    def update_record(self, record_id: int, data: RecordUpdateRequest, current_user: User) -> RecordResponse:
        record = self._get_or_404(record_id)
        self._check_ownership_or_admin(record, current_user)

        updates = data.model_dump(exclude_none=True)
        updated = self.repo.update(record, **updates)
        return RecordResponse.model_validate(updated)

    def delete_record(self, record_id: int, current_user: User) -> dict:
        record = self._get_or_404(record_id)
        self._check_ownership_or_admin(record, current_user)

        self.repo.soft_delete(record)
        return {"message": f"Record {record_id} has been deleted"}

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _get_or_404(self, record_id: int) -> FinancialRecord:
        record = self.repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial record with id {record_id} not found",
            )
        return record

    def _check_ownership_or_admin(self, record: FinancialRecord, user: User) -> None:
        """Only the record's creator or an admin can modify/delete it."""
        from app.models.user import UserRole
        if record.created_by != user.id and user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this record",
            )
