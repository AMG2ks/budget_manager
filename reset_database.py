#!/usr/bin/env python3
"""
Reset Database Script for Smart Budget Manager
This script will delete all existing data and create a fresh, clean database.
"""

import os
import sys
from pathlib import Path

# Add the budget_manager module to the path
sys.path.insert(0, str(Path(__file__).parent))

from budget_manager.core.database import DatabaseManager
from budget_manager.services.budget_service import BudgetService
from budget_manager.services.expense_service import ExpenseService
from budget_manager.services.recommendation_service import RecommendationService


def reset_database():
    """Reset the database by deleting the file and creating clean tables."""
    print("🗑️  Resetting Smart Budget Manager Database...")
    print("=" * 50)
    
    # Get the database path
    data_dir = Path.home() / ".budget_manager"
    db_path = data_dir / "budget.db"
    
    # Delete existing database file if it exists
    if db_path.exists():
        print(f"📁 Found existing database at: {db_path}")
        print("🗑️  Deleting existing database...")
        db_path.unlink()
        print("✅ Database deleted successfully!")
    else:
        print("📝 No existing database found.")
    
    # Create fresh database with clean tables
    print("🔧 Creating fresh database...")
    db_manager = DatabaseManager()
    print("✅ Clean database created successfully!")
    
    # Test the database by checking table creation
    print("🧪 Testing database connection...")
    try:
        # Initialize services to test database
        budget_service = BudgetService(db_manager)
        expense_service = ExpenseService(db_manager)
        recommendation_service = RecommendationService(db_manager)
        
        # Test basic operations
        income_entries = budget_service.get_income_entries()
        all_expenses = expense_service.get_expenses()
        savings_goals = budget_service.get_all_savings_goals()
        
        print(f"📊 Database status:")
        print(f"  - Income entries: {len(income_entries)}")
        print(f"  - Expenses: {len(all_expenses)}")
        print(f"  - Savings goals: {len(savings_goals)}")
        print("✅ Database is ready for use!")
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False
    
    print("")
    print("🎉 Database reset completed successfully!")
    print("")
    print("📋 Next steps:")
    print("1. Launch the web interface: streamlit run app.py")
    print("2. Or use the CLI: python -m budget_manager --help")
    print("3. Start by setting your monthly income and savings goals")
    print("")
    print("💰 Happy budgeting!")
    
    return True


if __name__ == "__main__":
    try:
        success = reset_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 