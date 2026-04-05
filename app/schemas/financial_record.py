from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.financial_record import RecordType


# ── Request schemas ──────────────────────────────────────────────────────────

class RecordCreateRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Must be a positive number")
    type: RecordType
    category: str = Field(..., min_length=1, max_length=100)
    date: date
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category must not be blank")
        return v.strip().lower()


class RecordUpdateRequest(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[RecordType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def category_strip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return v.strip().lower()
        return v


# ── Filter schema (used as query parameters) ─────────────────────────────────

class RecordFilterParams(BaseModel):
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


# ── Response schemas ─────────────────────────────────────────────────────────

class RecordResponse(BaseModel):
    id: int
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedRecordsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[RecordResponse]
