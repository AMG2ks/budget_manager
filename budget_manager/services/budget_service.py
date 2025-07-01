"""
Budget service for managing income entries and savings goals.
Multi-user support with data isolation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ..core.database import DatabaseManager
from ..core.models import BudgetEntry, IncomeEntryDB, SavingsGoal, SavingsGoalDB


class BudgetService:
    """Service for managing budget entries and savings goals with user isolation."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize budget service.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def add_income(self, user_id: int, amount: Decimal, month: date, description: str = None) -> BudgetEntry:
        """
        Add a monthly income entry for a specific user.
        
        Args:
            user_id: ID of the user
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
        
        with self.db_manager.get_session() as session:
            # Check if income entry already exists for this user and month
            existing_entry = session.query(IncomeEntryDB).filter_by(
                user_id=user_id,
                month=month
            ).first()
            
            if existing_entry:
                # Update existing entry
                existing_entry.amount = amount
                existing_entry.description = description
                session.commit()
                session.refresh(existing_entry)
                
                return BudgetEntry(
                    id=existing_entry.id,
                    amount=existing_entry.amount,
                    month=existing_entry.month,
                    description=existing_entry.description,
                    created_at=existing_entry.created_at
                )
            else:
                # Create new entry
                db_entry = IncomeEntryDB(
                    user_id=user_id,
                    amount=amount,
                    month=month,
                    description=description
                )
                
                session.add(db_entry)
                session.commit()
                session.refresh(db_entry)
                
                return BudgetEntry(
                    id=db_entry.id,
                    amount=db_entry.amount,
                    month=db_entry.month,
                    description=db_entry.description,
                    created_at=db_entry.created_at
                )
    
    def get_monthly_income(self, user_id: int, month: date) -> Decimal:
        """
        Get total income for a specific user and month.
        
        Args:
            user_id: ID of the user
            month: Month to get income for
            
        Returns:
            Total income amount for the month
        """
        month = month.replace(day=1)
        
        with self.db_manager.get_session() as session:
            entry = session.query(IncomeEntryDB).filter_by(
                user_id=user_id,
                month=month
            ).first()
            
            return entry.amount if entry else Decimal('0')
    
    def get_income_entries(self, user_id: int, start_month: date = None, end_month: date = None) -> List[BudgetEntry]:
        """
        Get income entries for a user within a date range.
        
        Args:
            user_id: ID of the user
            start_month: Start month (inclusive). If None, no start limit.
            end_month: End month (inclusive). If None, no end limit.
            
        Returns:
            List of BudgetEntry objects
        """
        with self.db_manager.get_session() as session:
            query = session.query(IncomeEntryDB).filter_by(user_id=user_id)
            
            if start_month:
                query = query.filter(IncomeEntryDB.month >= start_month.replace(day=1))
            if end_month:
                query = query.filter(IncomeEntryDB.month <= end_month.replace(day=1))
            
            entries = query.order_by(IncomeEntryDB.month.desc()).all()
            
            return [
                BudgetEntry(
                    id=entry.id,
                    amount=entry.amount,
                    month=entry.month,
                    description=entry.description,
                    created_at=entry.created_at
                )
                for entry in entries
            ]
    
    def update_income(self, user_id: int, entry_id: int, amount: Decimal = None, description: str = None) -> Optional[BudgetEntry]:
        """
        Update an existing income entry for a user.
        
        Args:
            user_id: ID of the user
            entry_id: ID of the entry to update
            amount: New amount (if provided)
            description: New description (if provided)
            
        Returns:
            Updated BudgetEntry or None if not found
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount is not None and amount <= 0:
            raise ValueError("Income amount must be positive")
        
        with self.db_manager.get_session() as session:
            entry = session.query(IncomeEntryDB).filter_by(
                id=entry_id,
                user_id=user_id
            ).first()
            
            if not entry:
                return None
            
            if amount is not None:
                entry.amount = amount
            if description is not None:
                entry.description = description
            
            session.commit()
            session.refresh(entry)
            
            return BudgetEntry(
                id=entry.id,
                amount=entry.amount,
                month=entry.month,
                description=entry.description,
                created_at=entry.created_at
            )
    
    def delete_income(self, user_id: int, entry_id: int) -> bool:
        """
        Delete an income entry for a user.
        
        Args:
            user_id: ID of the user
            entry_id: ID of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.db_manager.get_session() as session:
            entry = session.query(IncomeEntryDB).filter_by(
                id=entry_id,
                user_id=user_id
            ).first()
            
            if entry:
                session.delete(entry)
                session.commit()
                return True
            
            return False
    
    def set_savings_goal(self, user_id: int, target_amount: Decimal, month: date, description: str = None) -> SavingsGoal:
        """
        Set a savings goal for a specific user and month.
        
        Args:
            user_id: ID of the user
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
        
        with self.db_manager.get_session() as session:
            # Check if goal already exists for this user and month
            existing_goal = session.query(SavingsGoalDB).filter_by(
                user_id=user_id,
                month=month
            ).first()
            
            if existing_goal:
                # Update existing goal
                existing_goal.target_amount = target_amount
                existing_goal.description = description
                session.commit()
                session.refresh(existing_goal)
                
                return SavingsGoal(
                    id=existing_goal.id,
                    target_amount=existing_goal.target_amount,
                    month=existing_goal.month,
                    description=existing_goal.description,
                    created_at=existing_goal.created_at
                )
            else:
                # Create new goal
                db_goal = SavingsGoalDB(
                    user_id=user_id,
                    target_amount=target_amount,
                    month=month,
                    description=description
                )
                
                session.add(db_goal)
                session.commit()
                session.refresh(db_goal)
                
                return SavingsGoal(
                    id=db_goal.id,
                    target_amount=db_goal.target_amount,
                    month=db_goal.month,
                    description=db_goal.description,
                    created_at=db_goal.created_at
                )
    
    def get_savings_goal(self, user_id: int, month: date) -> Optional[SavingsGoal]:
        """
        Get savings goal for a specific user and month.
        
        Args:
            user_id: ID of the user
            month: Month to get goal for
            
        Returns:
            SavingsGoal or None if not found
        """
        month = month.replace(day=1)
        
        with self.db_manager.get_session() as session:
            goal = session.query(SavingsGoalDB).filter_by(
                user_id=user_id,
                month=month
            ).first()
            
            if goal:
                return SavingsGoal(
                    id=goal.id,
                    target_amount=goal.target_amount,
                    month=goal.month,
                    description=goal.description,
                    created_at=goal.created_at
                )
            
            return None
    
    def get_all_savings_goals(self, user_id: int) -> List[SavingsGoal]:
        """
        Get all savings goals for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of SavingsGoal objects
        """
        with self.db_manager.get_session() as session:
            goals = session.query(SavingsGoalDB).filter_by(
                user_id=user_id
            ).order_by(SavingsGoalDB.month.desc()).all()
            
            return [
                SavingsGoal(
                    id=goal.id,
                    target_amount=goal.target_amount,
                    month=goal.month,
                    description=goal.description,
                    created_at=goal.created_at
                )
                for goal in goals
            ]
    
    def delete_savings_goal(self, user_id: int, goal_id: int) -> bool:
        """
        Delete a savings goal for a user.
        
        Args:
            user_id: ID of the user
            goal_id: ID of the goal to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.db_manager.get_session() as session:
            goal = session.query(SavingsGoalDB).filter_by(
                id=goal_id,
                user_id=user_id
            ).first()
            
            if goal:
                session.delete(goal)
                session.commit()
                return True
            
            return False 