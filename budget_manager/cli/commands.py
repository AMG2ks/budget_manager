"""
Command-line interface commands for the budget manager.
"""

import traceback
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn

from ..core.models import ExpenseCategory
from ..services.budget_service import BudgetService  
from ..services.expense_service import ExpenseService
from ..services.recommendation_service import RecommendationService
from ..utils.date_utils import DateUtils
from ..utils.formatters import Formatters

# Initialize Rich console for beautiful output
console = Console()

# Create the main CLI app
app = typer.Typer(help="Smart Budget Manager - Manage your finances intelligently")

# Sub-commands
salary_app = typer.Typer(help="Manage salary/income entries")
expense_app = typer.Typer(help="Manage daily expenses")
goal_app = typer.Typer(help="Manage savings goals")
report_app = typer.Typer(help="Generate reports and analytics")

# Add sub-commands to main app
app.add_typer(salary_app, name="salary")
app.add_typer(expense_app, name="expense")
app.add_typer(goal_app, name="goal")
app.add_typer(report_app, name="report")

# Initialize services
budget_service = BudgetService()
expense_service = ExpenseService()
recommendation_service = RecommendationService()


class BudgetCLI:
    """Budget manager CLI interface."""
    
    @staticmethod
    def run():
        """Run the CLI application."""
        app()


def handle_error(func):
    """Decorator to handle common errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            console.print(f"[dim]Details: {traceback.format_exc()}[/dim]")
            raise typer.Exit(1)
    return wrapper


# ============= MAIN COMMANDS =============

@app.command()
@handle_error
def init():
    """Initialize the budget manager application."""
    console.print("[green]✅ Budget Manager initialized successfully![/green]")
    console.print("[dim]Database created at ~/.budget_manager/budget.db[/dim]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("1. Set your monthly salary: [cyan]budget-manager salary set 5000[/cyan]")
    console.print("2. Set your savings goal: [cyan]budget-manager goal set 1000[/cyan]")
    console.print("3. Add expenses: [cyan]budget-manager expense add 25.50 'Lunch' --category food[/cyan]")
    console.print("4. Get recommendations: [cyan]budget-manager recommend[/cyan]")


@app.command()
@handle_error
def recommend():
    """Get daily spending recommendation."""
    rec = recommendation_service.get_daily_recommendation()
    
    if not rec:
        console.print("[yellow]⚠️ Cannot generate recommendations[/yellow]")
        console.print("Please ensure you have:")
        console.print("• Set your monthly income: [cyan]budget-manager salary set AMOUNT[/cyan]")
        console.print("• Set your savings goal: [cyan]budget-manager goal set AMOUNT[/cyan]")
        return
    
    # Create recommendation panel
    rec_lines = Formatters.format_recommendation_summary(rec)
    rec_text = "\n".join(rec_lines)
    
    console.print(Panel(rec_text, title="💡 Daily Spending Recommendation", title_align="left"))
    
    # Show alerts
    alerts = recommendation_service.get_smart_alerts()
    if alerts:
        console.print("\n[yellow]📢 Smart Alerts:[/yellow]")
        for alert in alerts:
            formatted_alert = Formatters.format_alert(alert)
            console.print(f"  {formatted_alert}")


@app.command()
@handle_error
def status():
    """Show current budget status."""
    summary = recommendation_service.get_monthly_summary()
    
    if not summary:
        console.print("[yellow]⚠️ No budget data available[/yellow]")
        console.print("Set up your income and start tracking expenses!")
        return
    
    # Format and display summary
    summary_lines = Formatters.format_budget_summary(summary)
    summary_text = "\n".join(summary_lines)
    
    console.print(Panel(summary_text, title="📊 Current Budget Status", title_align="left"))
    
    # Show savings progress
    progress = recommendation_service.get_savings_progress()
    if progress:
        console.print(f"\n[green]🎯 Savings Progress: {progress['progress_percentage']:.1f}%[/green]")
        
        # Progress bar
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress_bar:
            task = progress_bar.add_task("Savings Goal", total=100)
            progress_bar.update(task, completed=progress['progress_percentage'])


# ============= SALARY COMMANDS =============

@salary_app.command("set")
@handle_error
def set_salary(
    amount: float = typer.Argument(..., help="Monthly salary amount"),
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Month (YYYY-MM format, default: current month)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Optional description")
):
    """Set monthly salary/income."""
    try:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
    except (InvalidOperation, ValueError) as e:
        console.print(f"[red]Invalid amount: {amount}[/red]")
        raise typer.Exit(1)
    
    # Parse month
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            console.print(f"[red]Invalid month format. Use YYYY-MM (e.g., 2023-12)[/red]")
            raise typer.Exit(1)
    else:
        month_date = date.today()
    
    # Add income entry
    entry = budget_service.add_income(amount_decimal, month_date, description)
    
    console.print(f"[green]✅ Salary set: {Formatters.format_currency(entry.amount)} for {DateUtils.format_month_year(entry.month)}[/green]")


@salary_app.command("show")
@handle_error
def show_salary(
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Month (YYYY-MM format, default: current month)")
):
    """Show salary for a specific month."""
    # Parse month
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            console.print(f"[red]Invalid month format. Use YYYY-MM (e.g., 2023-12)[/red]")
            raise typer.Exit(1)
    else:
        month_date = date.today()
    
    total_income = budget_service.get_monthly_income(month_date)
    entries = budget_service.get_income_entries(start_month=month_date, end_month=month_date)
    
    console.print(f"[cyan]💵 Income for {DateUtils.format_month_year(month_date)}:[/cyan]")
    console.print(f"Total: [green]{Formatters.format_currency(total_income)}[/green]")
    
    if entries:
        console.print("\nEntries:")
        for entry in entries:
            desc = f" - {entry.description}" if entry.description else ""
            console.print(f"  • {Formatters.format_currency(entry.amount)}{desc}")


# ============= EXPENSE COMMANDS =============

@expense_app.command("add")
@handle_error
def add_expense(
    amount: float = typer.Argument(..., help="Expense amount"),
    description: str = typer.Argument(..., help="Expense description"),
    category: ExpenseCategory = typer.Option(ExpenseCategory.OTHER, "--category", "-c", help="Expense category"),
    date_str: Optional[str] = typer.Option(None, "--date", "-d", help="Expense date (YYYY-MM-DD, default: today)")
):
    """Add a new expense."""
    try:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
    except (InvalidOperation, ValueError):
        console.print(f"[red]Invalid amount: {amount}[/red]")
        raise typer.Exit(1)
    
    # Parse date
    expense_date = date.today()
    if date_str:
        try:
            expense_date = DateUtils.parse_date_string(date_str)
        except ValueError:
            console.print(f"[red]Invalid date format. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)
    
    # Add expense
    expense = expense_service.add_expense(amount_decimal, description, category, expense_date)
    
    console.print(f"[green]✅ Expense added: {Formatters.format_currency(expense.amount)} - {expense.description} ({expense.category.value})[/green]")
    
    # Show updated recommendation
    rec = recommendation_service.get_daily_recommendation()
    if rec:
        console.print(f"[dim]💡 Updated daily limit: {Formatters.format_currency(rec.recommended_daily_limit)}[/dim]")


@expense_app.command("list")
@handle_error
def list_expenses(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of expenses to show"),
    category: Optional[ExpenseCategory] = typer.Option(None, "--category", "-c", help="Filter by category"),
    days: Optional[int] = typer.Option(None, "--days", "-d", help="Show expenses from last N days")
):
    """List recent expenses."""
    # Calculate date range
    start_date = None
    if days:
        start_date = date.today() - timedelta(days=days)
    
    expenses = expense_service.get_expenses(
        start_date=start_date,
        category=category,
        limit=limit
    )
    
    if not expenses:
        console.print("[yellow]No expenses found[/yellow]")
        return
    
    # Create table
    table = Table(title="Recent Expenses")
    table.add_column("Date", style="cyan")
    table.add_column("Amount", style="green")
    table.add_column("Description", style="white")
    table.add_column("Category", style="magenta")
    
    total = Decimal('0')
    for expense in expenses:
        table.add_row(
            expense.expense_date.strftime("%Y-%m-%d"),
            Formatters.format_currency(expense.amount),
            Formatters.truncate_text(expense.description, 30),
            expense.category.value.title()
        )
        total += expense.amount
    
    console.print(table)
    console.print(f"\n[green]Total: {Formatters.format_currency(total)}[/green]")


@expense_app.command("today")
@handle_error
def today_expenses():
    """Show today's expenses."""
    expenses = expense_service.get_today_expenses()
    
    if not expenses:
        console.print("[yellow]No expenses recorded today[/yellow]")
        return
    
    console.print(f"[cyan]💸 Today's Expenses ({date.today().strftime('%Y-%m-%d')}):[/cyan]")
    
    total = Decimal('0')
    for expense in expenses:
        console.print(f"  • {Formatters.format_currency(expense.amount)} - {expense.description} ({expense.category.value})")
        total += expense.amount
    
    console.print(f"\n[green]Total today: {Formatters.format_currency(total)}[/green]")
    
    # Show remaining daily budget
    rec = recommendation_service.get_daily_recommendation()
    if rec:
        remaining = rec.recommended_daily_limit - total
        if remaining >= 0:
            console.print(f"[green]Remaining budget: {Formatters.format_currency(remaining)}[/green]")
        else:
            console.print(f"[red]Over budget by: {Formatters.format_currency(abs(remaining))}[/red]")


# ============= GOAL COMMANDS =============

@goal_app.command("set")
@handle_error
def set_goal(
    amount: float = typer.Argument(..., help="Monthly savings target amount"),
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Month (YYYY-MM format, default: current month)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Optional description")
):
    """Set monthly savings goal."""
    try:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
    except (InvalidOperation, ValueError):
        console.print(f"[red]Invalid amount: {amount}[/red]")
        raise typer.Exit(1)
    
    # Parse month
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            console.print(f"[red]Invalid month format. Use YYYY-MM (e.g., 2023-12)[/red]")
            raise typer.Exit(1)
    else:
        month_date = date.today()
    
    # Set savings goal
    goal = budget_service.set_savings_goal(amount_decimal, month_date, description)
    
    console.print(f"[green]✅ Savings goal set: {Formatters.format_currency(goal.target_amount)} for {DateUtils.format_month_year(goal.month)}[/green]")


@goal_app.command("show")
@handle_error
def show_goal(
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Month (YYYY-MM format, default: current month)")
):
    """Show savings goal for a specific month."""
    # Parse month
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            console.print(f"[red]Invalid month format. Use YYYY-MM (e.g., 2023-12)[/red]")
            raise typer.Exit(1)
    else:
        month_date = date.today()
    
    goal = budget_service.get_savings_goal(month_date)
    
    if not goal:
        console.print(f"[yellow]No savings goal set for {DateUtils.format_month_year(month_date)}[/yellow]")
        console.print(f"Set one with: [cyan]budget-manager goal set AMOUNT[/cyan]")
        return
    
    console.print(f"[cyan]🎯 Savings Goal for {DateUtils.format_month_year(goal.month)}:[/cyan]")
    console.print(f"Target: [green]{Formatters.format_currency(goal.target_amount)}[/green]")
    if goal.description:
        console.print(f"Description: {goal.description}")


# ============= REPORT COMMANDS =============

@report_app.command("monthly")
@handle_error  
def monthly_report(
    month: Optional[str] = typer.Option(None, "--month", "-m", help="Month (YYYY-MM format, default: current month)")
):
    """Generate monthly budget report."""
    # Parse month
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m").date()
        except ValueError:
            console.print(f"[red]Invalid month format. Use YYYY-MM (e.g., 2023-12)[/red]")
            raise typer.Exit(1)
    else:
        month_date = date.today()
    
    summary = recommendation_service.get_monthly_summary(month_date)
    
    if not summary:
        console.print(f"[yellow]No data available for {DateUtils.format_month_year(month_date)}[/yellow]")
        return
    
    # Display comprehensive report
    summary_lines = Formatters.format_budget_summary(summary)
    summary_text = "\n".join(summary_lines)
    
    console.print(Panel(summary_text, title=f"📊 Monthly Report - {DateUtils.format_month_year(month_date)}", title_align="left"))


@report_app.command("category")
@handle_error
def category_report(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
):
    """Generate category spending analysis."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    analysis = recommendation_service.analyze_spending_patterns(start_date, end_date)
    
    if not analysis:
        console.print(f"[yellow]No expenses found in the last {days} days[/yellow]")
        return
    
    console.print(f"[cyan]📊 Category Analysis (Last {days} days)[/cyan]")
    console.print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")
    
    # Create table
    table = Table(title="Spending by Category")
    table.add_column("Category", style="cyan")
    table.add_column("Total", style="green")
    table.add_column("Count", style="yellow")  
    table.add_column("Average", style="blue")
    table.add_column("Percentage", style="magenta")
    
    # Sort by total amount (highest first)
    sorted_analysis = sorted(analysis.items(), key=lambda x: x[1]['total'], reverse=True)
    
    for category, data in sorted_analysis:
        table.add_row(
            category.title(),
            Formatters.format_currency(data['total']),
            str(data['count']),
            Formatters.format_currency(data['average']),
            Formatters.format_percentage(float(data['percentage']))
        )
    
    console.print(table)


if __name__ == "__main__":
    app() 