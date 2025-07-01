"""
Budget calculation logic for smart spending recommendations.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional
from calendar import monthrange

from .models import BudgetEntry, Expense, SavingsGoal, DailyRecommendation, BudgetSummary


class BudgetCalculator:
    """Handles all budget calculations and recommendations."""
    
    def calculate_daily_recommendation(
        self,
        monthly_income: Decimal,
        savings_target: Decimal,
        current_month_expenses: List[Expense],
        target_date: date = None
    ) -> DailyRecommendation:
        """
        Calculate daily spending recommendation to meet savings target.
        
        Args:
            monthly_income: Total monthly income
            savings_target: Desired monthly savings amount
            current_month_expenses: List of expenses for current month
            target_date: Target date to achieve savings (default: 3rd of next month)
            
        Returns:
            DailyRecommendation with recommended daily spending limit
        """
        today = date.today()
        
        # Default target date is 3rd of next month
        if target_date is None:
            if today.month == 12:
                target_date = date(today.year + 1, 1, 3)
            else:
                target_date = date(today.year, today.month + 1, 3)
        
        # Calculate days remaining until target
        days_remaining = (target_date - today).days
        if days_remaining <= 0:
            days_remaining = 1  # At least one day to avoid division by zero
        
        # Calculate total spent this month
        current_month_spent = sum(
            expense.amount for expense in current_month_expenses
            if expense.expense_date.month == today.month and expense.expense_date.year == today.year
        )
        
        # Calculate available budget for spending
        available_for_spending = monthly_income - savings_target
        
        # Calculate remaining budget
        remaining_budget = available_for_spending - current_month_spent
        
        # Calculate recommended daily limit
        recommended_daily_limit = max(Decimal('0'), remaining_budget / Decimal(str(days_remaining)))
        
        # Calculate projected savings if recommendation is followed
        projected_total_expenses = current_month_spent + (recommended_daily_limit * Decimal(str(days_remaining)))
        projected_savings = monthly_income - projected_total_expenses
        
        return DailyRecommendation(
            recommended_daily_limit=recommended_daily_limit,
            days_remaining=days_remaining,
            current_month_spent=current_month_spent,
            savings_target=savings_target,
            monthly_income=monthly_income,
            projected_savings=projected_savings
        )
    
    def calculate_monthly_summary(
        self,
        month: date,
        income_entries: List[BudgetEntry],
        expenses: List[Expense],
        savings_goal: Optional[SavingsGoal] = None
    ) -> BudgetSummary:
        """
        Calculate comprehensive monthly budget summary.
        
        Args:
            month: Month to summarize (day will be ignored)
            income_entries: List of income entries for the month
            expenses: List of expenses for the month
            savings_goal: Optional savings goal for the month
            
        Returns:
            BudgetSummary with comprehensive month analysis
        """
        # Filter entries for the specific month
        month_start = month.replace(day=1)
        
        # Calculate total income for the month
        total_income = sum(
            entry.amount for entry in income_entries
            if entry.month.month == month.month and entry.month.year == month.year
        )
        
        # Calculate total expenses for the month
        month_expenses = [
            expense for expense in expenses
            if expense.expense_date.month == month.month and expense.expense_date.year == month.year
        ]
        total_expenses = sum(expense.amount for expense in month_expenses)
        
        # Group expenses by category
        expense_by_category: Dict[str, Decimal] = {}
        for expense in month_expenses:
            category = expense.category.value if hasattr(expense.category, 'value') else str(expense.category)
            expense_by_category[category] = expense_by_category.get(category, Decimal('0')) + expense.amount
        
        # Calculate savings
        actual_savings = total_income - total_expenses
        savings_target = savings_goal.target_amount if savings_goal else Decimal('0')
        
        # Calculate days
        days_in_month = monthrange(month.year, month.month)[1]
        today = date.today()
        if month.month == today.month and month.year == today.year:
            days_passed = today.day
        elif month < today.replace(day=1):
            days_passed = days_in_month
        else:
            days_passed = 0
        
        return BudgetSummary(
            month=month_start,
            total_income=total_income,
            total_expenses=total_expenses,
            savings_target=savings_target,
            actual_savings=actual_savings,
            expense_by_category=expense_by_category,
            days_in_month=days_in_month,
            days_passed=days_passed
        )
    
    def calculate_category_spending_analysis(
        self, 
        expenses: List[Expense],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Analyze spending patterns by category.
        
        Args:
            expenses: List of expenses to analyze
            start_date: Start date for analysis (optional)
            end_date: End date for analysis (optional)
            
        Returns:
            Dictionary with category analysis including total, average, percentage
        """
        # Filter expenses by date range if provided
        if start_date or end_date:
            filtered_expenses = []
            for expense in expenses:
                if start_date and expense.expense_date < start_date:
                    continue
                if end_date and expense.expense_date > end_date:
                    continue
                filtered_expenses.append(expense)
            expenses = filtered_expenses
        
        if not expenses:
            return {}
        
        # Calculate total spending
        total_spending = sum(expense.amount for expense in expenses)
        
        # Group by category
        category_totals: Dict[str, Decimal] = {}
        category_counts: Dict[str, int] = {}
        
        for expense in expenses:
            category = expense.category.value if hasattr(expense.category, 'value') else str(expense.category)
            category_totals[category] = category_totals.get(category, Decimal('0')) + expense.amount
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate analysis
        analysis = {}
        for category, total in category_totals.items():
            count = category_counts[category]
            average = total / Decimal(str(count)) if count > 0 else Decimal('0')
            percentage = (total / total_spending * Decimal('100')) if total_spending > 0 else Decimal('0')
            
            analysis[category] = {
                'total': total,
                'count': count,
                'average': average,
                'percentage': percentage
            }
        
        return analysis
    
    def predict_monthly_outcome(
        self,
        monthly_income: Decimal,
        current_expenses: List[Expense],
        daily_spending_rate: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Predict end-of-month financial outcome based on current spending patterns.
        
        Args:
            monthly_income: Monthly income amount
            current_expenses: Current month expenses
            daily_spending_rate: Override daily spending rate (optional)
            
        Returns:
            Dictionary with predicted totals and savings
        """
        today = date.today()
        days_in_month = monthrange(today.year, today.month)[1]
        days_passed = today.day
        days_remaining = days_in_month - days_passed
        
        # Calculate current total spending
        current_total = sum(
            expense.amount for expense in current_expenses
            if expense.expense_date.month == today.month and expense.expense_date.year == today.year
        )
        
        # Calculate daily spending rate if not provided
        if daily_spending_rate is None and days_passed > 0:
            daily_spending_rate = current_total / Decimal(str(days_passed))
        elif daily_spending_rate is None:
            daily_spending_rate = Decimal('0')
        
        # Predict remaining spending
        predicted_remaining = daily_spending_rate * Decimal(str(days_remaining))
        predicted_total_expenses = current_total + predicted_remaining
        predicted_savings = monthly_income - predicted_total_expenses
        
        return {
            'current_expenses': current_total,
            'predicted_remaining_expenses': predicted_remaining,
            'predicted_total_expenses': predicted_total_expenses,
            'predicted_savings': predicted_savings,
            'daily_spending_rate': daily_spending_rate
        } 