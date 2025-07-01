"""
Tests for the budget calculator functionality.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from budget_manager.core.calculator import BudgetCalculator
from budget_manager.core.models import BudgetEntry, Expense, SavingsGoal, ExpenseCategory


class TestBudgetCalculator:
    """Test cases for BudgetCalculator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = BudgetCalculator()
        self.today = date.today()
        
        # Sample data
        self.monthly_income = Decimal('5000')
        self.savings_target = Decimal('1000')
        self.sample_expenses = [
            Expense(
                amount=Decimal('25.50'),
                description="Lunch",
                category=ExpenseCategory.FOOD,
                date=self.today
            ),
            Expense(
                amount=Decimal('50.00'),
                description="Gas",
                category=ExpenseCategory.TRANSPORTATION,
                date=self.today
            )
        ]
    
    def test_daily_recommendation_calculation(self):
        """Test daily spending recommendation calculation."""
        recommendation = self.calculator.calculate_daily_recommendation(
            monthly_income=self.monthly_income,
            savings_target=self.savings_target,
            current_month_expenses=self.sample_expenses
        )
        
        assert recommendation is not None
        assert recommendation.monthly_income == self.monthly_income
        assert recommendation.savings_target == self.savings_target
        assert recommendation.current_month_spent == Decimal('75.50')
        assert recommendation.recommended_daily_limit >= Decimal('0')
        assert recommendation.days_remaining > 0
    
    def test_monthly_summary_calculation(self):
        """Test monthly budget summary calculation."""
        # Create sample budget entry
        budget_entries = [
            BudgetEntry(
                amount=self.monthly_income,
                month=self.today,
                description="Salary"
            )
        ]
        
        # Create savings goal
        savings_goal = SavingsGoal(
            target_amount=self.savings_target,
            month=self.today,
            description="Monthly savings"
        )
        
        summary = self.calculator.calculate_monthly_summary(
            month=self.today,
            income_entries=budget_entries,
            expenses=self.sample_expenses,
            savings_goal=savings_goal
        )
        
        assert summary is not None
        assert summary.total_income == self.monthly_income
        assert summary.total_expenses == Decimal('75.50')
        assert summary.savings_target == self.savings_target
        assert summary.actual_savings == self.monthly_income - Decimal('75.50')
        assert len(summary.expense_by_category) > 0
    
    def test_category_spending_analysis(self):
        """Test category spending analysis."""
        analysis = self.calculator.calculate_category_spending_analysis(
            expenses=self.sample_expenses
        )
        
        assert len(analysis) == 2  # food and transportation
        assert 'food' in analysis
        assert 'transportation' in analysis
        
        # Check food category
        food_analysis = analysis['food']
        assert food_analysis['total'] == Decimal('25.50')
        assert food_analysis['count'] == 1
        assert food_analysis['average'] == Decimal('25.50')
        
        # Check transportation category
        transport_analysis = analysis['transportation']
        assert transport_analysis['total'] == Decimal('50.00')
        assert transport_analysis['count'] == 1
        assert transport_analysis['average'] == Decimal('50.00')
    
    def test_predict_monthly_outcome(self):
        """Test monthly outcome prediction."""
        prediction = self.calculator.predict_monthly_outcome(
            monthly_income=self.monthly_income,
            current_expenses=self.sample_expenses
        )
        
        assert prediction is not None
        assert 'current_expenses' in prediction
        assert 'predicted_remaining_expenses' in prediction
        assert 'predicted_total_expenses' in prediction
        assert 'predicted_savings' in prediction
        assert 'daily_spending_rate' in prediction
        
        assert prediction['current_expenses'] == Decimal('75.50')
        assert prediction['predicted_savings'] <= self.monthly_income 