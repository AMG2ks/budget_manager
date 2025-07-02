#!/usr/bin/env python3
"""
Multi-User Demo Script for Budget Manager
Creates multiple test users and sample data to demonstrate multi-user capabilities.
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal

from budget_manager.services.auth_service import AuthService, AuthenticationError
from budget_manager.services.expense_service import ExpenseService
from budget_manager.services.budget_service import BudgetService
from budget_manager.core.models import UserCreate, IncomeEntryCreate, ExpenseCreate, SavingsGoalCreate


def create_demo_users():
    """Create demo users with sample data."""
    auth_service = AuthService()
    
    # Demo users to create
    users = [
        {
            "username": "alice_smith",
            "email": "alice@example.com",
            "full_name": "Alice Smith",
            "password": "demo123",
            "income": 5000.00,
            "savings_goal": 1000.00,
            "expenses": [
                (50.00, "Groceries", "food"),
                (25.00, "Lunch", "food"),
                (15.00, "Coffee", "food"),
                (100.00, "Utilities", "utilities"),
                (30.00, "Gas", "transportation"),
            ]
        },
        {
            "username": "bob_johnson",
            "email": "bob@example.com", 
            "full_name": "Bob Johnson",
            "password": "demo123",
            "income": 4200.00,
            "savings_goal": 800.00,
            "expenses": [
                (35.00, "Dinner", "food"),
                (20.00, "Snacks", "food"),
                (80.00, "Internet", "utilities"),
                (45.00, "Bus Pass", "transportation"),
                (60.00, "Entertainment", "entertainment"),
            ]
        },
        {
            "username": "carol_davis",
            "email": "carol@example.com",
            "full_name": "Carol Davis", 
            "password": "demo123",
            "income": 6000.00,
            "savings_goal": 1500.00,
            "expenses": [
                (75.00, "Weekly Shopping", "food"),
                (40.00, "Restaurant", "food"),
                (120.00, "Phone Bill", "utilities"),
                (200.00, "Car Payment", "transportation"),
                (90.00, "Gym Membership", "health"),
            ]
        },
        {
            "username": "david_wilson",
            "email": "david@example.com",
            "full_name": "David Wilson",
            "password": "demo123", 
            "income": 3800.00,
            "savings_goal": 600.00,
            "expenses": [
                (30.00, "Lunch", "food"),
                (10.00, "Coffee", "food"),
                (70.00, "Electricity", "utilities"),
                (25.00, "Uber", "transportation"),
                (40.00, "Movies", "entertainment"),
            ]
        }
    ]
    
    created_users = []
    
    print("🎭 Creating Demo Users for Multi-User Testing")
    print("=" * 50)
    
    for user_data in users:
        try:
            # Create user
            user_create = UserCreate(
                username=user_data["username"],
                email=user_data["email"], 
                full_name=user_data["full_name"],
                password=user_data["password"]
            )
            
            # Check if user already exists
            existing_user = auth_service.get_user_by_username(user_data["username"])
            if existing_user:
                print(f"⚠️  User '{user_data['username']}' already exists, skipping...")
                created_users.append(existing_user)
                continue
            
            # Register the user
            user_profile = auth_service.register_user(user_create)
            created_users.append(user_profile)
            print(f"✅ Created user: {user_profile.full_name} (@{user_profile.username})")
            
            # Add sample financial data for this user
            budget_service = BudgetService(user_id=user_profile.id)
            expense_service = ExpenseService(user_id=user_profile.id)
            
            # Add monthly income
            income_entry = IncomeEntryCreate(
                amount=Decimal(str(user_data["income"])),
                source="Monthly Salary",
                month=datetime.now().month,
                year=datetime.now().year,
                description="Demo monthly salary"
            )
            budget_service.add_income_entry(income_entry)
            
            # Add savings goal  
            savings_goal = SavingsGoalCreate(
                target_amount=Decimal(str(user_data["savings_goal"])),
                target_month=datetime.now().month,
                target_year=datetime.now().year,
                description="Monthly savings target"
            )
            budget_service.add_savings_goal(savings_goal)
            
            # Add sample expenses over the last few days
            base_date = datetime.now() - timedelta(days=5)
            for i, (amount, desc, category) in enumerate(user_data["expenses"]):
                expense_date = base_date + timedelta(days=i % 6)
                expense = ExpenseCreate(
                    amount=Decimal(str(amount)),
                    description=desc,
                    category=category,
                    date=expense_date
                )
                expense_service.add_expense(expense)
            
            print(f"   💰 Added income: ${user_data['income']:,.2f}")
            print(f"   🎯 Added savings goal: ${user_data['savings_goal']:,.2f}")
            print(f"   📊 Added {len(user_data['expenses'])} sample expenses")
            
        except AuthenticationError as e:
            print(f"❌ Failed to create user '{user_data['username']}': {e}")
            continue
        except Exception as e:
            print(f"❌ Unexpected error creating user '{user_data['username']}': {e}")
            continue
    
    print("\n" + "=" * 50)
    print(f"🎉 Multi-User Demo Setup Complete!")
    print(f"✅ {len(created_users)} users ready for testing")
    print("\n📋 Demo User Credentials:")
    print("Username: alice_smith | Password: demo123")
    print("Username: bob_johnson | Password: demo123") 
    print("Username: carol_davis | Password: demo123")
    print("Username: david_wilson | Password: demo123")
    print("\n🚀 Start the web app with: streamlit run app.py")
    print("💡 Try logging in as different users to see data isolation!")
    
    return created_users


def show_user_stats():
    """Display statistics for all users."""
    auth_service = AuthService()
    
    try:
        stats = auth_service.get_system_stats()
        users = auth_service.get_all_users()
        
        print("\n📊 Multi-User System Statistics")
        print("=" * 40)
        print(f"👥 Total Users: {stats['total_users']}")
        print(f"💰 Total Income Entries: {stats['total_income_entries']}")
        print(f"💸 Total Expenses: {stats['total_expenses']}")
        print(f"🎯 Total Savings Goals: {stats['total_savings_goals']}")
        
        print("\n👥 User Details:")
        print("-" * 40)
        for user in users:
            user_stats = auth_service.get_user_stats(user.id)
            if user_stats:
                print(f"• {user.full_name} (@{user.username})")
                print(f"  Income Entries: {user_stats['income_entries']}")
                print(f"  Expenses: {user_stats['total_expenses']}") 
                print(f"  Goals: {user_stats['savings_goals']}")
                print(f"  Days Active: {user_stats['days_since_registration']}")
                print()
        
    except Exception as e:
        print(f"❌ Error getting user stats: {e}")


def main():
    """Main function."""
    print("🎭 Budget Manager - Multi-User Demo")
    print("Creating demo users to showcase multi-user capabilities...\n")
    
    try:
        # Create demo users
        created_users = create_demo_users()
        
        # Show statistics
        show_user_stats()
        
        print("\n🎯 What to Test:")
        print("1. Login as different users to see data isolation")
        print("2. Check that each user has their own financial data")
        print("3. Try adding expenses/income as different users")
        print("4. View the Multi-User tab in Settings to see all users")
        print("5. Test concurrent access with multiple browser tabs")
        
        print("\n💡 The SQLite database supports multiple users simultaneously!")
        print("   Each user's data is completely isolated and secure.")
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 