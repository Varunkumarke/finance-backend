from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_analyst_or_admin, require_any_role
from app.models.financial_record import RecordType
from app.models.user import User
from app.repositories.record_repository import FinancialRecordRepository
from app.schemas.dashboard import (
    CategoryTotal,
    DashboardSummaryResponse,
    MonthlyTrend,
    RecentActivity,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role),
):
    """
    Full dashboard summary: totals, category breakdowns, trends, recent activity.
    Accessible to all authenticated roles (viewer, analyst, admin).
    """
    repo = FinancialRecordRepository(db)

    total_income = repo.get_total_by_type(RecordType.income)
    total_expenses = repo.get_total_by_type(RecordType.expense)
    net_balance = total_income - total_expenses

    income_by_category = [
        CategoryTotal(**row) for row in repo.get_totals_by_category(RecordType.income)
    ]
    expense_by_category = [
        CategoryTotal(**row) for row in repo.get_totals_by_category(RecordType.expense)
    ]

    monthly_trends = [MonthlyTrend(**row) for row in repo.get_monthly_trends()]

    recent_records = repo.get_recent(limit=10)
    recent_activity = [
        RecentActivity(
            id=r.id,
            amount=r.amount,
            type=r.type.value,
            category=r.category,
            date=str(r.date),
            notes=r.notes,
        )
        for r in recent_records
    ]

    return DashboardSummaryResponse(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        total_records=repo.get_total_count(),
        income_by_category=income_by_category,
        expense_by_category=expense_by_category,
        monthly_trends=monthly_trends,
        recent_activity=recent_activity,
    )


@router.get("/insights", dependencies=[Depends(require_analyst_or_admin)])
def get_insights(db: Session = Depends(get_db)):
    """
    Advanced insights — top spending categories, income vs expense ratio.
    Requires: analyst or admin role.
    """
    repo = FinancialRecordRepository(db)

    total_income = repo.get_total_by_type(RecordType.income)
    total_expenses = repo.get_total_by_type(RecordType.expense)

    top_expense_categories = repo.get_totals_by_category(RecordType.expense)[:5]
    top_income_categories = repo.get_totals_by_category(RecordType.income)[:5]

    ratio = round(total_expenses / total_income, 4) if total_income > 0 else None

    return {
        "expense_to_income_ratio": ratio,
        "interpretation": (
            "Spending more than earning" if ratio and ratio > 1
            else "Healthy — earning more than spending" if ratio
            else "No income recorded yet"
        ),
        "top_expense_categories": top_expense_categories,
        "top_income_categories": top_income_categories,
    }
