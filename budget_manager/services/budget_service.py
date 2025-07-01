"""
Budget service for managing income entries and savings goals.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from ..core.database import DatabaseManager
from ..core.models import BudgetEntry, BudgetEntryDB, SavingsGoal, SavingsGoalDB


class BudgetService:
    """Service for managing budget entries and savings goals."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize budget service.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db = db_manager or DatabaseManager()
    
    def add_income(self, amount: Decimal, month: date, description: str = None) -> BudgetEntry:
        """
        Add a monthly income entry.
        
        Args:
            amount: Income amount
            month: Month for the income (day will be set to 1st)
            description: Optional description
            
        Returns:
            Created BudgetEntry
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Income amount must be positive")
        
        # Normalize month to first day
        month = month.replace(day=1)
        
        # Create database record
        db_entry = BudgetEntryDB(
            amount=amount,
            month=month,
            description=description
        )
        
        created_entry_data = self.db.create(db_entry)
        
        # Convert to Pydantic model
        return BudgetEntry(**created_entry_data)
    
    def get_monthly_income(self, month: date) -> Decimal:
        """
        Get total income for a specific month.
        
        Args:
            month: Month to get income for
            
        Returns:
            Total income amount for the month
        """
        month = month.replace(day=1)
        entries = self.db.filter_by(BudgetEntryDB, month=month)
        return sum(entry['amount'] for entry in entries)
    
    def get_income_entries(self, start_month: date = None, end_month: date = None) -> List[BudgetEntry]:
        """
        Get income entries within a date range.
        
        Args:
            start_month: Start month (inclusive). If None, no start limit.
            end_month: End month (inclusive). If None, no end limit.
            
        Returns:
            List of BudgetEntry objects
        """
        all_entries = self.db.get_all(BudgetEntryDB)
        
        # Filter by date range if specified
        filtered_entries = []
        for entry_data in all_entries:
            if start_month and entry_data['month'] < start_month.replace(day=1):
                continue
            if end_month and entry_data['month'] > end_month.replace(day=1):
                continue
            filtered_entries.append(entry_data)
        
        # Convert to Pydantic models
        return [
            BudgetEntry(**entry_data)
            for entry_data in filtered_entries
        ]
    
    def update_income(self, entry_id: int, amount: Decimal = None, description: str = None) -> Optional[BudgetEntry]:
        """
        Update an existing income entry.
        
        Args:
            entry_id: ID of the entry to update
            amount: New amount (if provided)
            description: New description (if provided)
            
        Returns:
            Updated BudgetEntry or None if not found
            
        Raises:
            ValueError: If amount is not positive
        """
        updates = {}
        if amount is not None:
            if amount <= 0:
                raise ValueError("Income amount must be positive")
            updates['amount'] = amount
        if description is not None:
            updates['description'] = description
        
        if not updates:
            # No updates provided, return current entry
            db_entry = self.db.get_by_id(BudgetEntryDB, entry_id)
            if db_entry:
                return BudgetEntry(
                    id=db_entry.id,
                    amount=db_entry.amount,
                    month=db_entry.month,
                    description=db_entry.description,
                    created_at=db_entry.created_at
                )
            return None
        
        updated_entry = self.db.update(BudgetEntryDB, entry_id, **updates)
        if updated_entry:
            return BudgetEntry(
                id=updated_entry.id,
                amount=updated_entry.amount,
                month=updated_entry.month,
                description=updated_entry.description,
                created_at=updated_entry.created_at
            )
        return None
    
    def delete_income(self, entry_id: int) -> bool:
        """
        Delete an income entry.
        
        Args:
            entry_id: ID of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.db.delete(BudgetEntryDB, entry_id)
    
    def set_savings_goal(self, target_amount: Decimal, month: date, description: str = None) -> SavingsGoal:
        """
        Set a savings goal for a specific month.
        
        Args:
            target_amount: Target savings amount
            month: Month for the goal (day will be set to 1st)
            description: Optional description
            
        Returns:
            Created SavingsGoal
            
        Raises:
            ValueError: If target amount is not positive
        """
        if target_amount <= 0:
            raise ValueError("Savings target must be positive")
        
        # Normalize month to first day
        month = month.replace(day=1)
        
        # Check if goal already exists for this month
        existing_goals = self.db.filter_by(SavingsGoalDB, month=month)
        if existing_goals:
            # Update existing goal
            updated_goal = self.db.update(
                SavingsGoalDB, 
                existing_goals[0]['id'],
                target_amount=target_amount,
                description=description
            )
            
            return SavingsGoal(**updated_goal)
        else:
            # Create new goal
            db_goal = SavingsGoalDB(
                target_amount=target_amount,
                month=month,
                description=description
            )
            
            created_goal_data = self.db.create(db_goal)
            
            return SavingsGoal(**created_goal_data)
    
    def get_savings_goal(self, month: date) -> Optional[SavingsGoal]:
        """
        Get savings goal for a specific month.
        
        Args:
            month: Month to get goal for
            
        Returns:
            SavingsGoal or None if not found
        """
        month = month.replace(day=1)
        goals = self.db.filter_by(SavingsGoalDB, month=month)
        
        if goals:
            goal_data = goals[0]  # Should be only one goal per month
            return SavingsGoal(**goal_data)
        return None
    
    def get_all_savings_goals(self) -> List[SavingsGoal]:
        """
        Get all savings goals.
        
        Returns:
            List of SavingsGoal objects
        """
        db_goals = self.db.get_all(SavingsGoalDB)
        
        return [
            SavingsGoal(**goal_data)
            for goal_data in db_goals
        ] 