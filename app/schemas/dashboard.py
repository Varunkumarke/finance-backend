from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category: str
    total: float


class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: float
    expense: float
    net: float


class RecentActivity(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: str
    notes: str | None


class DashboardSummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    total_records: int
    income_by_category: list[CategoryTotal]
    expense_by_category: list[CategoryTotal]
    monthly_trends: list[MonthlyTrend]
    recent_activity: list[RecentActivity]
