"""
Data models for the budget management application.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict
from enum import Enum

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, Date, DECIMAL, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ExpenseCategory(str, Enum):
    """Predefined expense categories."""
    
    FOOD = "food"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    SHOPPING = "shopping"
    HEALTH = "health"
    EDUCATION = "education"
    OTHER = "other"


class BudgetEntryDB(Base):
    """Database model for budget entries (salary/income)."""
    
    __tablename__ = "budget_entries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    month = Column(Date, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class ExpenseDB(Base):
    """Database model for expenses."""
    
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)


class SavingsGoalDB(Base):
    """Database model for savings goals."""
    
    __tablename__ = "savings_goals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_amount = Column(DECIMAL(10, 2), nullable=False)
    month = Column(Date, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic models for API/business logic
class BudgetEntry(BaseModel):
    """Budget entry model for salary/income tracking."""
    
    id: Optional[int] = None
    amount: Decimal = Field(..., gt=0, description="Income amount")
    month: date = Field(..., description="Month this income applies to")
    description: Optional[str] = Field(None, max_length=255)
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
    @validator("amount", pre=True)
    def validate_amount(cls, v):
        """Ensure amount is a positive decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class Expense(BaseModel):
    """Expense model for daily expense tracking."""
    
    id: Optional[int] = None
    amount: Decimal = Field(..., gt=0, description="Expense amount")
    description: str = Field(..., min_length=1, max_length=255)
    category: ExpenseCategory = Field(..., description="Expense category")
    expense_date: date = Field(default_factory=date.today, description="Expense date", alias="date")
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
    @validator("amount", pre=True)
    def validate_amount(cls, v):
        """Ensure amount is a positive decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class SavingsGoal(BaseModel):
    """Savings goal model for monthly targets."""
    
    id: Optional[int] = None
    target_amount: Decimal = Field(..., gt=0, description="Target savings amount")
    month: date = Field(..., description="Target month")
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        
    @validator("target_amount", pre=True)
    def validate_target_amount(cls, v):
        """Ensure target amount is a positive decimal."""
        if isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class DailyRecommendation(BaseModel):
    """Daily spending recommendation model."""
    
    recommended_daily_limit: Decimal = Field(..., description="Recommended daily spending limit")
    days_remaining: int = Field(..., description="Days remaining until target date")
    current_month_spent: Decimal = Field(..., description="Amount spent this month")
    savings_target: Decimal = Field(..., description="Monthly savings target")
    monthly_income: Decimal = Field(..., description="Monthly income")
    projected_savings: Decimal = Field(..., description="Projected savings if recommendation followed")
    
    class Config:
        from_attributes = True


class BudgetSummary(BaseModel):
    """Monthly budget summary model."""
    
    month: date = Field(..., description="Summary month")
    total_income: Decimal = Field(..., description="Total income for the month")
    total_expenses: Decimal = Field(..., description="Total expenses for the month")
    savings_target: Decimal = Field(..., description="Savings target for the month")
    actual_savings: Decimal = Field(..., description="Actual savings achieved")
    expense_by_category: Dict[str, Decimal] = Field(..., description="Expenses grouped by category")
    days_in_month: int = Field(..., description="Total days in the month")
    days_passed: int = Field(..., description="Days passed in the month")
    
    class Config:
        from_attributes = True 