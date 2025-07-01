#!/usr/bin/env python3
"""
Test script for multi-user functionality in Smart Budget Manager.
"""

import os
import sys
from datetime import date
from decimal import Decimal

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from budget_manager.services.auth_service import AuthService, AuthenticationError
from budget_manager.services.budget_service import BudgetService
from budget_manager.services.expense_service import ExpenseService
from budget_manager.core.models import UserCreate, UserLogin, ExpenseCategory


def test_multi_user_system():
    """Test multi-user functionality with data isolation."""
    
    print("🧪 Testing Multi-User Smart Budget Manager")
    print("=" * 50)
    
    # Initialize services
    auth_service = AuthService()
    budget_service = BudgetService()
    expense_service = ExpenseService()
    
    try:
        # Test 1: Create two users
        print("\n1️⃣ Creating test users...")
        
        user1_data = UserCreate(
            username="alice_test",
            email="alice@test.com",
            password="password123",
            full_name="Alice Test"
        )
        
        user2_data = UserCreate(
            username="bob_test", 
            email="bob@test.com",
            password="password456",
            full_name="Bob Test"
        )
        
        try:
            user1 = auth_service.register_user(user1_data)
            print(f"✅ Created user: {user1.username} ({user1.email})")
        except AuthenticationError as e:
            if "already exists" in str(e):
                print(f"ℹ️ User alice_test already exists, attempting login...")
                user1 = auth_service.login_user(UserLogin(username="alice_test", password="password123"))
            else:
                raise
        
        try:
            user2 = auth_service.register_user(user2_data)
            print(f"✅ Created user: {user2.username} ({user2.email})")
        except AuthenticationError as e:
            if "already exists" in str(e):
                print(f"ℹ️ User bob_test already exists, attempting login...")
                user2 = auth_service.login_user(UserLogin(username="bob_test", password="password456"))
            else:
                raise
        
        # Test 2: Add income for both users
        print("\n2️⃣ Adding income for both users...")
        
        alice_income = budget_service.add_income(
            user_id=user1.id,
            amount=Decimal('5000.00'),
            month=date.today(),
            description="Alice's salary"
        )
        print(f"✅ Added income for Alice: $5000.00")
        
        bob_income = budget_service.add_income(
            user_id=user2.id,
            amount=Decimal('4500.00'),
            month=date.today(),
            description="Bob's salary"
        )
        print(f"✅ Added income for Bob: $4500.00")
        
        # Test 3: Add expenses for both users
        print("\n3️⃣ Adding expenses for both users...")
        
        alice_expense = expense_service.add_expense(
            user_id=user1.id,
            amount=Decimal('50.00'),
            description="Alice's lunch",
            category=ExpenseCategory.FOOD
        )
        print(f"✅ Added expense for Alice: $50.00 (Food)")
        
        bob_expense = expense_service.add_expense(
            user_id=user2.id,
            amount=Decimal('75.00'),
            description="Bob's gas",
            category=ExpenseCategory.TRANSPORTATION
        )
        print(f"✅ Added expense for Bob: $75.00 (Transportation)")
        
        # Test 4: Verify data isolation
        print("\n4️⃣ Verifying data isolation...")
        
        # Check Alice's data
        alice_income_total = budget_service.get_monthly_income(user1.id, date.today())
        alice_expenses = expense_service.get_expenses(user1.id)
        
        print(f"✅ Alice's data:")
        print(f"   - Income: ${alice_income_total}")
        print(f"   - Expenses: {len(alice_expenses)} items")
        
        # Check Bob's data
        bob_income_total = budget_service.get_monthly_income(user2.id, date.today())
        bob_expenses = expense_service.get_expenses(user2.id)
        
        print(f"✅ Bob's data:")
        print(f"   - Income: ${bob_income_total}")
        print(f"   - Expenses: {len(bob_expenses)} items")
        
        # Test 5: Verify no cross-user data access
        print("\n5️⃣ Testing data isolation (should show no cross-contamination)...")
        
        # Alice should only see her own expenses
        alice_only_expenses = expense_service.get_expenses(user1.id)
        alice_food_expenses = [e for e in alice_only_expenses if e.category == ExpenseCategory.FOOD]
        alice_transport_expenses = [e for e in alice_only_expenses if e.category == ExpenseCategory.TRANSPORTATION]
        
        print(f"✅ Alice sees {len(alice_food_expenses)} food expenses (should be >= 1)")
        print(f"✅ Alice sees {len(alice_transport_expenses)} transport expenses (should be 0)")
        
        # Bob should only see his own expenses
        bob_only_expenses = expense_service.get_expenses(user2.id)
        bob_food_expenses = [e for e in bob_only_expenses if e.category == ExpenseCategory.FOOD]
        bob_transport_expenses = [e for e in bob_only_expenses if e.category == ExpenseCategory.TRANSPORTATION]
        
        print(f"✅ Bob sees {len(bob_food_expenses)} food expenses (should be 0)")
        print(f"✅ Bob sees {len(bob_transport_expenses)} transport expenses (should be >= 1)")
        
        # Test 6: Verify data counts
        print("\n6️⃣ Final verification...")
        assert alice_income_total == Decimal('5000.00'), f"Alice income mismatch: {alice_income_total}"
        assert bob_income_total == Decimal('4500.00'), f"Bob income mismatch: {bob_income_total}"
        assert len(alice_food_expenses) >= 1, f"Alice should have food expenses: {len(alice_food_expenses)}"
        assert len(alice_transport_expenses) == 0, f"Alice should have no transport expenses: {len(alice_transport_expenses)}"
        assert len(bob_food_expenses) == 0, f"Bob should have no food expenses: {len(bob_food_expenses)}"
        assert len(bob_transport_expenses) >= 1, f"Bob should have transport expenses: {len(bob_transport_expenses)}"
        
        print("\n" + "=" * 50)
        print("🎉 All multi-user tests passed successfully!")
        print("✅ Users can register and login")
        print("✅ Data is properly isolated between users")
        print("✅ All services work with user authentication")
        print("✅ No cross-user data leakage detected")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting multi-user test...")
    success = test_multi_user_system()
    print(f"\n📊 Test result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1) 