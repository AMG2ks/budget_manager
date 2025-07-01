"""
Data models for the budget management application.
Multi-user support with authentication and data isolation.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict
from enum import Enum
import hashlib
import secrets

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, Date, DECIMAL, Text, ForeignKey, UniqueConstraint, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

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


# SQLAlchemy Database Models
class User(Base):
    """User model for authentication and data isolation."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    salt: Mapped[str] = mapped_column(String(32), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    income_entries: Mapped[List["IncomeEntryDB"]] = relationship("IncomeEntryDB", back_populates="user", cascade="all, delete-orphan")
    expenses: Mapped[List["ExpenseDB"]] = relationship("ExpenseDB", back_populates="user", cascade="all, delete-orphan")
    savings_goals: Mapped[List["SavingsGoalDB"]] = relationship("SavingsGoalDB", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.salt = secrets.token_hex(16)
        self.password_hash = self._hash_password(password, self.salt)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches stored hash."""
        return self.password_hash == self._hash_password(password, self.salt)
    
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class IncomeEntryDB(Base):
    """Database model for monthly income entries."""
    __tablename__ = "income_entries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="income_entries")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'month', name='_user_month_income_uc'),
    )


class ExpenseDB(Base):
    """Database model for individual expense records."""
    __tablename__ = "expenses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[ExpenseCategory] = mapped_column(SQLEnum(ExpenseCategory), nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="expenses")


class SavingsGoalDB(Base):
    """Database model for monthly savings goals."""
    __tablename__ = "savings_goals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="savings_goals")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'month', name='_user_month_goal_uc'),
    )


# Pydantic models for API/business logic
class UserCreate(BaseModel):
    """Model for user creation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator("email")
    def validate_email(cls, v):
        """Basic email validation."""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @validator("username")
    def validate_username(cls, v):
        """Username validation."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()


class UserLogin(BaseModel):
    """Model for user login."""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserProfile(BaseModel):
    """Model for user profile information."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


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