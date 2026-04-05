from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_active_user, require_analyst_or_admin, require_any_role
from app.models.financial_record import RecordType
from app.models.user import User
from app.schemas.financial_record import (
    PaginatedRecordsResponse,
    RecordCreateRequest,
    RecordFilterParams,
    RecordResponse,
    RecordUpdateRequest,
)
from app.services.record_service import FinancialRecordService

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post("/", response_model=RecordResponse, status_code=201)
def create_record(
    data: RecordCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Create a new financial record.
    Requires: analyst or admin role.
    """
    return FinancialRecordService(db).create_record(data, current_user)


@router.get("/", response_model=PaginatedRecordsResponse)
def list_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role),
    type: Optional[RecordType] = Query(None, description="Filter by income or expense"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
):
    """
    List financial records with optional filtering and pagination.
    Accessible to all authenticated roles.
    """
    filters = RecordFilterParams(
        type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    return FinancialRecordService(db).get_records(filters)


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role),
):
    """
    Get a single financial record by ID.
    Accessible to all authenticated roles.
    """
    return FinancialRecordService(db).get_record(record_id)


@router.patch("/{record_id}", response_model=RecordResponse)
def update_record(
    record_id: int,
    data: RecordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Update a financial record.
    Requires: analyst or admin role.
    Analysts can only edit their own records; admins can edit any record.
    """
    return FinancialRecordService(db).update_record(record_id, data, current_user)


@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Soft-delete a financial record (hidden but not removed from DB).
    Requires: analyst or admin role.
    Analysts can only delete their own records; admins can delete any.
    """
    return FinancialRecordService(db).delete_record(record_id, current_user)
