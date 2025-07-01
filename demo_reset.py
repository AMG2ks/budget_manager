#!/usr/bin/env python3
"""
Demo Script - Reset Functionality for Smart Budget Manager
This script demonstrates the reset functionality both via CLI and programmatically.
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

# Add the budget_manager module to the path
sys.path.insert(0, str(Path(__file__).parent))

from budget_manager.services.budget_service import BudgetService
from budget_manager.services.expense_service import ExpenseService
from budget_manager.core.models import ExpenseCategory
from budget_manager.utils.formatters import Formatters


def demo_reset_functionality():
    """Demonstrate the reset functionality."""
    print("🧪 Demo: Reset Functionality")
    print("=" * 40)
    
    # Initialize services
    budget_service = BudgetService()
    expense_service = ExpenseService()
    
    print("\n1. 📊 Adding sample data...")
    
    # Add some sample data
    try:
        # Add income
        income = budget_service.add_income(
            amount=Decimal('4000'),
            month=date.today(),
            description="Demo salary"
        )
        print(f"   ✅ Added income: {Formatters.format_currency(income.amount)}")
        
        # Add expenses
        expense1 = expense_service.add_expense(
            amount=Decimal('25.50'),
            description="Demo lunch",
            category=ExpenseCategory.FOOD,
            expense_date=date.today()
        )
        
        expense2 = expense_service.add_expense(
            amount=Decimal('15.00'),
            description="Demo coffee",
            category=ExpenseCategory.FOOD,
            expense_date=date.today()
        )
        
        print(f"   ✅ Added expense: {Formatters.format_currency(expense1.amount)} - {expense1.description}")
        print(f"   ✅ Added expense: {Formatters.format_currency(expense2.amount)} - {expense2.description}")
        
        # Add savings goal
        goal = budget_service.set_savings_goal(
            target_amount=Decimal('1000'),
            month=date.today(),
            description="Demo savings goal"
        )
        print(f"   ✅ Added savings goal: {Formatters.format_currency(goal.target_amount)}")
        
    except Exception as e:
        print(f"   ❌ Error adding sample data: {e}")
        return
    
    print("\n2. 📋 Current database status:")
    
    # Show current data
    income_entries = budget_service.get_income_entries()
    all_expenses = expense_service.get_expenses()
    savings_goals = budget_service.get_all_savings_goals()
    
    print(f"   📊 Income entries: {len(income_entries)}")
    print(f"   💸 Expenses: {len(all_expenses)}")
    print(f"   🎯 Savings goals: {len(savings_goals)}")
    
    print("\n3. 🗑️  Demonstrating reset options:")
    print("   Option 1: Web Interface")
    print("     - Go to Settings → Data Management → Reset Database")
    print("     - Check both confirmation boxes")
    print("     - Click 'RESET DATABASE' button")
    print("")
    print("   Option 2: CLI Script")
    print("     - Run: python reset_database.py")
    print("")
    print("   Option 3: Make command")
    print("     - Run: make reset")
    print("")
    print("   Option 4: Manual deletion")
    print("     - Run: rm ~/.budget_manager/budget.db")
    
    print("\n4. 🔧 For this demo, let's reset using the script:")
    
    # Ask for confirmation in demo
    response = input("\n   Do you want to reset the database now? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        try:
            # Import reset functionality
            import os
            
            # Get database path
            data_dir = Path.home() / ".budget_manager"
            db_path = data_dir / "budget.db"
            
            # Delete database
            if db_path.exists():
                os.remove(db_path)
                print("   ✅ Database deleted")
            
            # Create fresh database
            from budget_manager.core.database import DatabaseManager
            DatabaseManager()
            print("   ✅ Fresh database created")
            
            # Verify reset
            new_budget_service = BudgetService()
            new_expense_service = ExpenseService()
            
            new_income_entries = new_budget_service.get_income_entries()
            new_expenses = new_expense_service.get_expenses()
            new_goals = new_budget_service.get_all_savings_goals()
            
            print("\n5. 📊 Database status after reset:")
            print(f"   📊 Income entries: {len(new_income_entries)}")
            print(f"   💸 Expenses: {len(new_expenses)}")
            print(f"   🎯 Savings goals: {len(new_goals)}")
            
            if len(new_income_entries) == 0 and len(new_expenses) == 0 and len(new_goals) == 0:
                print("\n   🎉 Reset successful! Database is now clean.")
            else:
                print("\n   ⚠️  Reset may not have completed fully.")
                
        except Exception as e:
            print(f"   ❌ Error during reset: {e}")
    else:
        print("   ℹ️  Reset cancelled. Data preserved.")
    
    print("\n🔄 Remember: You can reset anytime using:")
    print("   - Web interface (Settings page)")
    print("   - python reset_database.py")
    print("   - make reset")
    
    print("\n💰 Demo complete!")


if __name__ == "__main__":
    demo_reset_functionality() 