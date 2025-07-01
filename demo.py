#!/usr/bin/env python3
"""
Demo script for the Smart Budget Manager.
This script demonstrates the core functionality of the budget management application.
"""

from datetime import date, timedelta
from decimal import Decimal

from budget_manager.services.budget_service import BudgetService
from budget_manager.services.expense_service import ExpenseService
from budget_manager.services.recommendation_service import RecommendationService
from budget_manager.core.models import ExpenseCategory
from budget_manager.utils.formatters import Formatters


def run_demo():
    """Run a comprehensive demo of the budget manager."""
    print("🚀 Smart Budget Manager Demo")
    print("=" * 50)
    
    # Initialize services
    budget_service = BudgetService()
    expense_service = ExpenseService()
    recommendation_service = RecommendationService()
    
    try:
        # 1. Set up monthly income
        print("\n1. Setting up monthly income...")
        monthly_salary = Decimal('5000')
        income_entry = budget_service.add_income(
            amount=monthly_salary,
            month=date.today(),
            description="Software Engineer Salary"
        )
        print(f"✅ Income set: {Formatters.format_currency(income_entry.amount)}")
        
        # 2. Set savings goal
        print("\n2. Setting savings goal...")
        savings_target = Decimal('1500')
        savings_goal = budget_service.set_savings_goal(
            target_amount=savings_target,
            month=date.today(),
            description="Emergency fund + investment"
        )
        print(f"🎯 Savings goal: {Formatters.format_currency(savings_goal.target_amount)}")
        
        # 3. Add some sample expenses
        print("\n3. Adding sample expenses...")
        sample_expenses = [
            (Decimal('35.50'), "Grocery shopping", ExpenseCategory.FOOD),
            (Decimal('12.00'), "Coffee and breakfast", ExpenseCategory.FOOD),
            (Decimal('45.00'), "Gas for car", ExpenseCategory.TRANSPORTATION),
            (Decimal('25.00'), "Movie tickets", ExpenseCategory.ENTERTAINMENT),
            (Decimal('150.00'), "Electricity bill", ExpenseCategory.UTILITIES),
            (Decimal('75.00'), "Clothing", ExpenseCategory.SHOPPING),
            (Decimal('20.00'), "Pharmacy", ExpenseCategory.HEALTH),
        ]
        
        for amount, description, category in sample_expenses:
            expense = expense_service.add_expense(
                amount=amount,
                description=description,
                category=category,
                expense_date=date.today() - timedelta(days=1)  # Yesterday
            )
            print(f"  • {Formatters.format_currency(expense.amount)} - {expense.description}")
        
        # 4. Get daily recommendation
        print("\n4. Getting smart recommendation...")
        recommendation = recommendation_service.get_daily_recommendation()
        
        if recommendation:
            rec_lines = Formatters.format_recommendation_summary(recommendation)
            print("\n💡 Daily Spending Recommendation:")
            for line in rec_lines:
                print(f"  {line}")
        else:
            print("❌ Could not generate recommendation")
        
        # 5. Show budget status
        print("\n5. Current budget status...")
        summary = recommendation_service.get_monthly_summary()
        
        if summary:
            summary_lines = Formatters.format_budget_summary(summary)
            print("\n📊 Budget Summary:")
            for line in summary_lines:
                print(f"  {line}")
        
        # 6. Show smart alerts
        print("\n6. Smart alerts...")
        alerts = recommendation_service.get_smart_alerts()
        
        if alerts:
            print("\n🔔 Smart Alerts:")
            for alert in alerts:
                formatted_alert = Formatters.format_alert(alert)
                print(f"  {formatted_alert}")
        else:
            print("✅ No alerts - you're doing great!")
        
        # 7. Category analysis
        print("\n7. Spending analysis...")
        analysis = recommendation_service.analyze_spending_patterns()
        
        if analysis:
            print("\n📈 Category Breakdown:")
            for category, data in analysis.items():
                percentage = float(data['percentage'])
                print(f"  • {category.title()}: {Formatters.format_currency(data['total'])} ({percentage:.1f}%)")
        
        # 8. Show savings progress
        print("\n8. Savings progress...")
        progress = recommendation_service.get_savings_progress()
        
        if progress:
            print(f"\n🎯 Savings Progress: {progress['progress_percentage']:.1f}%")
            print(f"   Current: {Formatters.format_currency(Decimal(str(progress['current_savings'])))}")
            print(f"   Target:  {Formatters.format_currency(Decimal(str(progress['target_amount'])))}")
            print(f"   On Track: {'✅ Yes' if progress['on_track'] else '❌ No'}")
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Try the CLI commands:")
        print("   python -m budget_manager recommend")
        print("   python -m budget_manager status")
        print("   python -m budget_manager expense add 25.50 'Lunch' --category food")
        print("   python -m budget_manager report monthly")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_demo() 