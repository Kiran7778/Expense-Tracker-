from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ───────── REQUEST MODELS ─────────

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    date: str
    description: Optional[str] = ""

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        datetime.strptime(v, "%Y-%m-%d")
        return v.strip()

    @field_validator("title", "category")
    @classmethod
    def strip(cls, v):
        return v.strip()


class ExpenseUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None


# ───────── RESPONSE MODELS ─────────

class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    date: str
    description: str
    created_at: str


class ExpenseListResponse(BaseModel):
    expenses: list[ExpenseResponse]
    count: int


class TotalResponse(BaseModel):
    total: float
    count: int


class CategorySummary(BaseModel):
    category: str
    total: float
    count: int


class SummaryResponse(BaseModel):
    total_spent: float
    total_count: int
    categories: list[CategorySummary]


class MessageResponse(BaseModel):
    message: str