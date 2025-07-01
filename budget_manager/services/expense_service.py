"""
Expense service for managing daily expenses and categories.
Multi-user support with data isolation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict

from sqlalchemy.orm import Session

from ..core.database import DatabaseManager
from ..core.models import Expense, ExpenseDB, ExpenseCategory


class ExpenseService:
    """Service for managing daily expenses with user isolation."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize expense service.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def add_expense(
        self, 
        user_id: int,
        amount: Decimal, 
        description: str, 
        category: ExpenseCategory, 
        expense_date: date = None
    ) -> Expense:
        """
        Add a new expense for a specific user.
        
        Args:
            user_id: ID of the user
            amount: Expense amount
            description: Description of the expense
            category: Expense category
            expense_date: Date of expense (defaults to today)
            
        Returns:
            Created Expense
            
        Raises:
            ValueError: If amount is not positive or description is empty
        """
        if amount <= 0:
            raise ValueError("Expense amount must be positive")
        
        if not description or not description.strip():
            raise ValueError("Expense description cannot be empty")
        
        if expense_date is None:
            expense_date = date.today()
        
        with self.db_manager.get_session() as session:
            # Create database record
            db_expense = ExpenseDB(
                user_id=user_id,
                amount=amount,
                description=description.strip(),
                category=category,
                expense_date=expense_date
            )
            
            session.add(db_expense)
            session.commit()
            session.refresh(db_expense)
            
            return Expense(
                id=db_expense.id,
                amount=db_expense.amount,
                description=db_expense.description,
                category=db_expense.category,
                expense_date=db_expense.expense_date,
                created_at=db_expense.created_at
            )
    
    def get_expenses(
        self, 
        user_id: int,
        start_date: date = None, 
        end_date: date = None,
        category: ExpenseCategory = None,
        limit: int = None
    ) -> List[Expense]:
        """
        Get expenses for a user with optional filtering.
        
        Args:
            user_id: ID of the user
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            category: Category filter
            limit: Maximum number of results
            
        Returns:
            List of Expense objects
        """
        with self.db_manager.get_session() as session:
            query = session.query(ExpenseDB).filter_by(user_id=user_id)
            
            if start_date:
                query = query.filter(ExpenseDB.expense_date >= start_date)
            if end_date:
                query = query.filter(ExpenseDB.expense_date <= end_date)
            if category:
                query = query.filter(ExpenseDB.category == category)
            
            query = query.order_by(ExpenseDB.expense_date.desc())
            
            if limit:
                query = query.limit(limit)
            
            expenses = query.all()
            
            return [
                Expense(
                    id=expense.id,
                    amount=expense.amount,
                    description=expense.description,
                    category=expense.category,
                    expense_date=expense.expense_date,
                    created_at=expense.created_at
                )
                for expense in expenses
            ]
    
    def get_monthly_expenses(self, user_id: int, month: date) -> List[Expense]:
        """
        Get all expenses for a specific user and month.
        
        Args:
            user_id: ID of the user
            month: Month to get expenses for
            
        Returns:
            List of Expense objects for the month
        """
        # Get start and end dates for the month
        start_date = month.replace(day=1)
        if month.month == 12:
            end_date = date(month.year + 1, 1, 1)
        else:
            end_date = date(month.year, month.month + 1, 1)
        
        return self.get_expenses(user_id=user_id, start_date=start_date, end_date=end_date)
    
    def get_today_expenses(self, user_id: int) -> List[Expense]:
        """
        Get expenses for today for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of today's expenses
        """
        today = date.today()
        return self.get_expenses(user_id=user_id, start_date=today, end_date=today)
    
    def get_expense_by_id(self, user_id: int, expense_id: int) -> Optional[Expense]:
        """
        Get a specific expense by ID for a user.
        
        Args:
            user_id: ID of the user
            expense_id: Expense ID
            
        Returns:
            Expense or None if not found
        """
        with self.db_manager.get_session() as session:
            expense = session.query(ExpenseDB).filter_by(
                id=expense_id,
                user_id=user_id
            ).first()
            
            if expense:
                return Expense(
                    id=expense.id,
                    amount=expense.amount,
                    description=expense.description,
                    category=expense.category,
                    expense_date=expense.expense_date,
                    created_at=expense.created_at
                )
            return None
    
    def update_expense(
        self, 
        user_id: int,
        expense_id: int, 
        amount: Decimal = None,
        description: str = None,
        category: ExpenseCategory = None,
        expense_date: date = None
    ) -> Optional[Expense]:
        """
        Update an existing expense for a user.
        
        Args:
            user_id: ID of the user
            expense_id: ID of the expense to update
            amount: New amount (if provided)
            description: New description (if provided)
            category: New category (if provided)
            expense_date: New date (if provided)
            
        Returns:
            Updated Expense or None if not found
            
        Raises:
            ValueError: If amount is not positive or description is empty
        """
        if amount is not None and amount <= 0:
            raise ValueError("Expense amount must be positive")
        
        if description is not None and not description.strip():
            raise ValueError("Expense description cannot be empty")
        
        with self.db_manager.get_session() as session:
            expense = session.query(ExpenseDB).filter_by(
                id=expense_id,
                user_id=user_id
            ).first()
            
            if not expense:
                return None
            
            if amount is not None:
                expense.amount = amount
            if description is not None:
                expense.description = description.strip()
            if category is not None:
                expense.category = category
            if expense_date is not None:
                expense.expense_date = expense_date
            
            session.commit()
            session.refresh(expense)
            
            return Expense(
                id=expense.id,
                amount=expense.amount,
                description=expense.description,
                category=expense.category,
                expense_date=expense.expense_date,
                created_at=expense.created_at
            )
    
    def delete_expense(self, user_id: int, expense_id: int) -> bool:
        """
        Delete an expense for a user.
        
        Args:
            user_id: ID of the user
            expense_id: ID of the expense to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.db_manager.get_session() as session:
            expense = session.query(ExpenseDB).filter_by(
                id=expense_id,
                user_id=user_id
            ).first()
            
            if expense:
                session.delete(expense)
                session.commit()
                return True
            
            return False
    
    def get_total_expenses(
        self, 
        user_id: int,
        start_date: date = None, 
        end_date: date = None,
        category: ExpenseCategory = None
    ) -> Decimal:
        """
        Get total expense amount for a user with optional filtering.
        
        Args:
            user_id: ID of the user
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            category: Category filter
            
        Returns:
            Total expense amount
        """
        expenses = self.get_expenses(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category=category
        )
        
        return sum(expense.amount for expense in expenses)
    
    def get_category_breakdown(
        self, 
        user_id: int,
        start_date: date = None, 
        end_date: date = None
    ) -> Dict[str, Decimal]:
        """
        Get expense breakdown by category for a user.
        
        Args:
            user_id: ID of the user
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Dictionary mapping category names to total amounts
        """
        expenses = self.get_expenses(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        breakdown = {}
        for expense in expenses:
            category_name = expense.category.value
            breakdown[category_name] = breakdown.get(category_name, Decimal('0')) + expense.amount
        
        return breakdown
    
    def get_available_categories(self) -> List[ExpenseCategory]:
        """
        Get all available expense categories.
        
        Returns:
            List of ExpenseCategory enum values
        """
        return list(ExpenseCategory) 