"""
Expense service for managing daily expenses and categories.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict

from ..core.database import DatabaseManager
from ..core.models import Expense, ExpenseDB, ExpenseCategory


class ExpenseService:
    """Service for managing daily expenses."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize expense service.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db = db_manager or DatabaseManager()
    
    def add_expense(
        self, 
        amount: Decimal, 
        description: str, 
        category: ExpenseCategory, 
        expense_date: date = None
    ) -> Expense:
        """
        Add a new expense.
        
        Args:
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
        
        # Create database record
        db_expense = ExpenseDB(
            amount=amount,
            description=description.strip(),
            category=category.value,
            date=expense_date
        )
        
        created_expense_data = self.db.create(db_expense)
        
        # Convert category and map date field
        created_expense_data['category'] = ExpenseCategory(created_expense_data['category'])
        created_expense_data['expense_date'] = created_expense_data.pop('date')
        
        # Convert to Pydantic model
        return Expense(**created_expense_data)
    
    def get_expenses(
        self, 
        start_date: date = None, 
        end_date: date = None,
        category: ExpenseCategory = None,
        limit: int = None
    ) -> List[Expense]:
        """
        Get expenses with optional filtering.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            category: Category filter
            limit: Maximum number of results
            
        Returns:
            List of Expense objects
        """
        if category:
            # Filter by category first
            db_expenses = self.db.filter_by(ExpenseDB, category=category.value)
        else:
            db_expenses = self.db.get_all(ExpenseDB, limit=limit)
        
        # Apply date filters
        filtered_expenses = []
        for expense_data in db_expenses:
            if start_date and expense_data['date'] < start_date:
                continue
            if end_date and expense_data['date'] > end_date:
                continue
            filtered_expenses.append(expense_data)
        
        # Apply limit if not already applied
        if limit and not category:
            filtered_expenses = filtered_expenses[:limit]
        elif limit and category:
            filtered_expenses = filtered_expenses[:limit]
        
        # Convert to Pydantic models
        return [
            Expense(
                id=expense_data['id'],
                amount=expense_data['amount'],
                description=expense_data['description'],
                category=ExpenseCategory(expense_data['category']),
                expense_date=expense_data['date'],
                created_at=expense_data['created_at']
            )
            for expense_data in filtered_expenses
        ]
    
    def get_monthly_expenses(self, month: date) -> List[Expense]:
        """
        Get all expenses for a specific month.
        
        Args:
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
        
        return self.get_expenses(start_date=start_date, end_date=end_date)
    
    def get_today_expenses(self) -> List[Expense]:
        """
        Get expenses for today.
        
        Returns:
            List of today's expenses
        """
        today = date.today()
        return self.get_expenses(start_date=today, end_date=today)
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Get a specific expense by ID.
        
        Args:
            expense_id: Expense ID
            
        Returns:
            Expense or None if not found
        """
        db_expense = self.db.get_by_id(ExpenseDB, expense_id)
        if db_expense:
            return Expense(
                id=db_expense.id,
                amount=db_expense.amount,
                description=db_expense.description,
                category=ExpenseCategory(db_expense.category),
                expense_date=db_expense.date,
                created_at=db_expense.created_at
            )
        return None
    
    def update_expense(
        self, 
        expense_id: int, 
        amount: Decimal = None,
        description: str = None,
        category: ExpenseCategory = None,
        expense_date: date = None
    ) -> Optional[Expense]:
        """
        Update an existing expense.
        
        Args:
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
        updates = {}
        
        if amount is not None:
            if amount <= 0:
                raise ValueError("Expense amount must be positive")
            updates['amount'] = amount
        
        if description is not None:
            if not description.strip():
                raise ValueError("Expense description cannot be empty")
            updates['description'] = description.strip()
        
        if category is not None:
            updates['category'] = category.value
        
        if expense_date is not None:
            updates['date'] = expense_date
        
        if not updates:
            # No updates provided, return current expense
            return self.get_expense_by_id(expense_id)
        
        updated_expense = self.db.update(ExpenseDB, expense_id, **updates)
        if updated_expense:
            return Expense(
                id=updated_expense.id,
                amount=updated_expense.amount,
                description=updated_expense.description,
                category=ExpenseCategory(updated_expense.category),
                expense_date=updated_expense.date,
                created_at=updated_expense.created_at
            )
        return None
    
    def delete_expense(self, expense_id: int) -> bool:
        """
        Delete an expense.
        
        Args:
            expense_id: ID of the expense to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.db.delete(ExpenseDB, expense_id)
    
    def get_total_expenses(
        self, 
        start_date: date = None, 
        end_date: date = None,
        category: ExpenseCategory = None
    ) -> Decimal:
        """
        Get total expense amount for a date range and/or category.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            category: Category filter
            
        Returns:
            Total expense amount
        """
        expenses = self.get_expenses(start_date=start_date, end_date=end_date, category=category)
        return sum(expense.amount for expense in expenses)
    
    def get_category_breakdown(
        self, 
        start_date: date = None, 
        end_date: date = None
    ) -> Dict[str, Decimal]:
        """
        Get expense breakdown by category.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Dictionary mapping category names to total amounts
        """
        expenses = self.get_expenses(start_date=start_date, end_date=end_date)
        
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