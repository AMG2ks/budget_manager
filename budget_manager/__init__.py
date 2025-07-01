"""
Smart Budget Manager

A comprehensive budget management application for tracking income, expenses,
and achieving savings goals through intelligent daily spending recommendations.
"""

__version__ = "1.0.0"
__author__ = "Budget Manager"
__email__ = "contact@budgetmanager.com"

from .core.models import BudgetEntry, Expense, SavingsGoal
from .services.budget_service import BudgetService
from .services.expense_service import ExpenseService
from .services.recommendation_service import RecommendationService

__all__ = [
    "BudgetEntry",
    "Expense", 
    "SavingsGoal",
    "BudgetService",
    "ExpenseService",
    "RecommendationService",
] 