"""
Recommendation service for generating smart budget recommendations.
Multi-user support with data isolation.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict

from ..core.calculator import BudgetCalculator
from ..core.models import DailyRecommendation, BudgetSummary
from .budget_service import BudgetService
from .expense_service import ExpenseService
from ..utils.formatters import Formatters


class RecommendationService:
    """Service for generating smart budget recommendations with user isolation."""
    
    def __init__(self, db_manager: Optional['DatabaseManager'] = None):
        """
        Initialize recommendation service.
        
        Args:
            db_manager: Database manager instance. If None, creates a new one.
        """
        from ..core.database import DatabaseManager
        db_manager = db_manager or DatabaseManager()
        
        self.calculator = BudgetCalculator()
        self.budget_service = BudgetService(db_manager)
        self.expense_service = ExpenseService(db_manager)
    
    def get_daily_recommendation(
        self, 
        user_id: int,
        target_date: date = None,
        month: date = None
    ) -> Optional[DailyRecommendation]:
        """
        Get daily spending recommendation for a specific user.
        
        Args:
            user_id: ID of the user
            target_date: Target date by which to achieve savings goal (defaults to 3rd of next month)
            month: Month to calculate for (defaults to current month)
            
        Returns:
            DailyRecommendation or None if insufficient data
        """
        if month is None:
            month = date.today()
        
        # Get monthly income
        monthly_income = self.budget_service.get_monthly_income(user_id, month)
        if monthly_income <= 0:
            return None  # No income data available
        
        # Get savings goal
        savings_goal = self.budget_service.get_savings_goal(user_id, month)
        if not savings_goal:
            return None  # No savings goal set
        
        # Get current month expenses
        current_expenses = self.expense_service.get_monthly_expenses(user_id, month)
        
        return self.calculator.calculate_daily_recommendation(
            monthly_income=monthly_income,
            savings_target=savings_goal.target_amount,
            current_month_expenses=current_expenses,
            target_date=target_date,
            current_month=month
        )
    
    def get_monthly_summary(self, user_id: int, month: date = None) -> Optional[BudgetSummary]:
        """
        Get monthly budget summary for a specific user.
        
        Args:
            user_id: ID of the user
            month: Month to summarize (defaults to current month)
            
        Returns:
            BudgetSummary or None if insufficient data
        """
        if month is None:
            month = date.today()
        
        # Get income entries
        income_entries = self.budget_service.get_income_entries(
            user_id=user_id,
            start_month=month, 
            end_month=month
        )
        
        # Get expenses
        expenses = self.expense_service.get_monthly_expenses(user_id, month)
        
        # Get savings goal
        savings_goal = self.budget_service.get_savings_goal(user_id, month)
        
        return self.calculator.calculate_monthly_summary(
            month=month,
            income_entries=income_entries,
            expenses=expenses,
            savings_goal=savings_goal
        )
    
    def analyze_spending_patterns(
        self, 
        user_id: int,
        start_date: date = None, 
        end_date: date = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Analyze spending patterns by category for a specific user.
        
        Args:
            user_id: ID of the user
            start_date: Start date for analysis (default: 30 days ago)
            end_date: End date for analysis (default: today)
            
        Returns:
            Dictionary with category analysis
        """
        if end_date is None:
            end_date = date.today()
        
        if start_date is None:
            # Default to 30 days ago
            start_date = date(end_date.year, end_date.month, 1)
            if start_date.month == 1:
                start_date = date(start_date.year - 1, 12, 1)
            else:
                start_date = date(start_date.year, start_date.month - 1, 1)
        
        # Get expenses for the period
        expenses = self.expense_service.get_expenses(
            user_id=user_id,
            start_date=start_date, 
            end_date=end_date
        )
        
        return self.calculator.calculate_category_spending_analysis(
            expenses=expenses,
            start_date=start_date,
            end_date=end_date
        )
    
    def predict_monthly_outcome(self, user_id: int, month: date = None) -> Optional[Dict[str, Decimal]]:
        """
        Predict end-of-month financial outcome for a specific user.
        
        Args:
            user_id: ID of the user
            month: Month to predict for (default: current month)
            
        Returns:
            Dictionary with predictions or None if insufficient data
        """
        if month is None:
            month = date.today()
        
        # Get monthly income
        monthly_income = self.budget_service.get_monthly_income(user_id, month)
        if monthly_income <= 0:
            return None  # No income data available
        
        # Get current month expenses
        current_expenses = self.expense_service.get_monthly_expenses(user_id, month)
        
        return self.calculator.predict_monthly_outcome(
            monthly_income=monthly_income,
            current_expenses=current_expenses
        )
    
    def get_smart_alerts(self, user_id: int, month: date = None) -> List[Dict[str, str]]:
        """
        Get smart alerts about spending and budget status for a specific user.
        
        Args:
            user_id: ID of the user
            month: Month to analyze (default: current month)
            
        Returns:
            List of alert dictionaries with 'type', 'message', and 'severity'
        """
        if month is None:
            month = date.today()
        
        alerts = []
        
        # Get recommendation and summary
        recommendation = self.get_daily_recommendation(user_id=user_id, month=month)
        summary = self.get_monthly_summary(user_id=user_id, month=month)
        prediction = self.predict_monthly_outcome(user_id=user_id, month=month)
        
        if not recommendation or not summary:
            alerts.append({
                'type': 'setup',
                'message': 'Please set up your monthly income and savings goal to get recommendations.',
                'severity': 'warning'
            })
            return alerts
        
        # Check if daily limit is very low
        if recommendation.recommended_daily_limit < Decimal('10'):
            limit_str = Formatters.format_currency(recommendation.recommended_daily_limit)
            alerts.append({
                'type': 'budget',
                'message': f'Your recommended daily limit is very low ({limit_str}). Consider adjusting your savings goal.',
                'severity': 'warning'
            })
        
        # Check if spending is on track
        if prediction:
            if prediction['predicted_savings'] < summary.savings_target:
                shortage = summary.savings_target - prediction['predicted_savings']
                shortage_str = Formatters.format_currency(shortage)
                alerts.append({
                    'type': 'savings',
                    'message': f'You may fall short of your savings goal by {shortage_str}. Consider reducing daily spending.',
                    'severity': 'error'
                })
            elif prediction['predicted_savings'] > summary.savings_target * Decimal('1.2'):
                excess = prediction['predicted_savings'] - summary.savings_target
                excess_str = Formatters.format_currency(excess)
                alerts.append({
                    'type': 'savings',
                    'message': f'Great job! You\'re on track to save {excess_str} more than your target.',
                    'severity': 'success'
                })
        
        # Check category spending
        today = date.today()
        if month.month == today.month and month.year == today.year:
            category_breakdown = self.expense_service.get_category_breakdown(
                user_id=user_id,
                start_date=month.replace(day=1),
                end_date=today
            )
            
            # Alert if any category is over 40% of total spending
            total_spent = sum(category_breakdown.values())
            if total_spent > 0:
                for category, amount in category_breakdown.items():
                    percentage = (amount / total_spent) * 100
                    if percentage > 40:
                        alerts.append({
                            'type': 'category',
                            'message': f'{category.title()} spending is {percentage:.1f}% of your budget. Consider diversifying expenses.',
                            'severity': 'info'
                        })
        
        # Check if approaching month end with high spending rate
        if recommendation.days_remaining <= 7 and recommendation.recommended_daily_limit < Decimal('5'):
            limit_str = Formatters.format_currency(recommendation.recommended_daily_limit)
            alerts.append({
                'type': 'timeline',
                'message': f'Only {recommendation.days_remaining} days left with {limit_str} daily limit. Stay focused!',
                'severity': 'warning'
            })
        
        return alerts
    
    def get_savings_progress(self, user_id: int, month: date = None) -> Optional[Dict[str, any]]:
        """
        Get savings progress information for a specific user.
        
        Args:
            user_id: ID of the user
            month: Month to analyze (default: current month)
            
        Returns:
            Dictionary with savings progress data
        """
        if month is None:
            month = date.today()
        
        summary = self.get_monthly_summary(user_id=user_id, month=month)
        if not summary:
            return None
        
        progress_percentage = 0
        if summary.savings_target > 0:
            progress_percentage = float((summary.actual_savings / summary.savings_target) * 100)
        
        return {
            'target_amount': float(summary.savings_target),
            'current_savings': float(summary.actual_savings),
            'progress_percentage': min(progress_percentage, 100),  # Cap at 100%
            'days_passed': summary.days_passed,
            'days_remaining': summary.days_in_month - summary.days_passed,
            'on_track': summary.actual_savings >= (summary.savings_target * (Decimal(str(summary.days_passed)) / Decimal(str(summary.days_in_month))))
        } 