"""
Formatting utilities for the budget manager.
"""

from decimal import Decimal
from typing import Dict, List, Any
from datetime import date


class Formatters:
    """Utility class for formatting data for display."""
    
    @staticmethod
    def format_currency(amount: Decimal, currency_symbol: str = None, 
                       decimal_places: int = None, group_thousands: bool = None) -> str:
        """
        Format decimal amount as currency using user preferences.
        
        Args:
            amount: Amount to format
            currency_symbol: Currency symbol to use (None = use user preference)
            decimal_places: Number of decimal places (None = use user preference)
            group_thousands: Whether to group thousands (None = use user preference)
            
        Returns:
            Formatted currency string
        """
        try:
            from ..core.user_preferences import get_user_preferences
            prefs = get_user_preferences()
            
            # Use user preferences if not specified
            if currency_symbol is None:
                currency_symbol = prefs.get_currency_symbol()
            if decimal_places is None:
                decimal_places = prefs.get_decimal_places()
            if group_thousands is None:
                group_thousands = prefs.get_group_thousands()
            
            # Format the number
            if group_thousands:
                formatted_amount = f"{amount:,.{decimal_places}f}"
            else:
                formatted_amount = f"{amount:.{decimal_places}f}"
            
            return f"{currency_symbol}{formatted_amount}"
            
        except ImportError:
            # Fallback if preferences not available
            return f"${amount:.2f}"
    
    @staticmethod
    def format_currency_input_label(base_label: str) -> str:
        """
        Format input labels with currency symbol.
        
        Args:
            base_label: Base label text
            
        Returns:
            Label with currency symbol
        """
        try:
            from ..core.user_preferences import get_user_preferences
            prefs = get_user_preferences()
            currency_code = prefs.get_currency_code()
            currency_symbol = prefs.get_currency_symbol()
            return f"{base_label} ({currency_code} {currency_symbol})"
        except ImportError:
            return f"{base_label} (USD $)"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 1) -> str:
        """
        Format float as percentage.
        
        Args:
            value: Value to format (e.g., 25.5 for 25.5%)
            decimal_places: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value:.{decimal_places}f}%"
    
    @staticmethod
    def format_category_breakdown(breakdown: Dict[str, Decimal]) -> List[str]:
        """
        Format category breakdown for display.
        
        Args:
            breakdown: Dictionary of category names to amounts
            
        Returns:
            List of formatted strings
        """
        if not breakdown:
            return ["No expenses recorded"]
        
        total = sum(breakdown.values())
        formatted_lines = []
        
        # Sort by amount (highest first)
        sorted_items = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_items:
            percentage = (amount / total * 100) if total > 0 else 0
            formatted_lines.append(
                f"  {category.title()}: {Formatters.format_currency(amount)} "
                f"({Formatters.format_percentage(percentage)})"
            )
        
        return formatted_lines
    
    @staticmethod
    def format_table_row(columns: List[str], widths: List[int]) -> str:
        """
        Format a table row with specified column widths.
        
        Args:
            columns: List of column values
            widths: List of column widths
            
        Returns:
            Formatted table row string
        """
        if len(columns) != len(widths):
            raise ValueError("Number of columns must match number of widths")
        
        formatted_columns = []
        for column, width in zip(columns, widths):
            formatted_columns.append(column[:width].ljust(width))
        
        return " | ".join(formatted_columns)
    
    @staticmethod
    def format_progress_bar(
        current: float, 
        target: float, 
        width: int = 20,
        filled_char: str = "█",
        empty_char: str = "░"
    ) -> str:
        """
        Format a progress bar.
        
        Args:
            current: Current value
            target: Target value
            width: Width of progress bar in characters
            filled_char: Character for filled portion
            empty_char: Character for empty portion
            
        Returns:
            Formatted progress bar string
        """
        if target <= 0:
            return empty_char * width
        
        progress = min(current / target, 1.0)  # Cap at 100%
        filled_width = int(progress * width)
        empty_width = width - filled_width
        
        return filled_char * filled_width + empty_char * empty_width
    
    @staticmethod
    def format_alert(alert: Dict[str, str]) -> str:
        """
        Format an alert message with appropriate styling indicators.
        
        Args:
            alert: Alert dictionary with 'type', 'message', and 'severity'
            
        Returns:
            Formatted alert string
        """
        severity_icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅'
        }
        
        icon = severity_icons.get(alert.get('severity', 'info'), 'ℹ️')
        message = alert.get('message', '')
        
        return f"{icon} {message}"
    
    @staticmethod
    def format_recommendation_summary(recommendation: Any) -> List[str]:
        """
        Format daily recommendation summary.
        
        Args:
            recommendation: DailyRecommendation object
            
        Returns:
            List of formatted summary lines
        """
        lines = [
            f"💰 Daily Spending Limit: {Formatters.format_currency(recommendation.recommended_daily_limit)}",
            f"📅 Days Remaining: {recommendation.days_remaining}",
            f"💸 Spent This Month: {Formatters.format_currency(recommendation.current_month_spent)}",
            f"🎯 Savings Target: {Formatters.format_currency(recommendation.savings_target)}",
            f"📊 Projected Savings: {Formatters.format_currency(recommendation.projected_savings)}"
        ]
        
        return lines
    
    @staticmethod
    def format_budget_summary(summary: Any) -> List[str]:
        """
        Format monthly budget summary.
        
        Args:
            summary: BudgetSummary object
            
        Returns:
            List of formatted summary lines
        """
        lines = [
            f"📊 Budget Summary for {summary.month.strftime('%B %Y')}",
            "=" * 40,
            f"💵 Total Income: {Formatters.format_currency(summary.total_income)}",
            f"💸 Total Expenses: {Formatters.format_currency(summary.total_expenses)}",
            f"💰 Actual Savings: {Formatters.format_currency(summary.actual_savings)}",
            f"🎯 Savings Target: {Formatters.format_currency(summary.savings_target)}",
            "",
            f"📅 Days: {summary.days_passed}/{summary.days_in_month}"
        ]
        
        # Add progress bar for savings
        if summary.savings_target > 0:
            progress_bar = Formatters.format_progress_bar(
                float(summary.actual_savings), 
                float(summary.savings_target)
            )
            progress_pct = (summary.actual_savings / summary.savings_target * 100)
            lines.append(f"Progress: {progress_bar} {progress_pct:.1f}%")
        
        # Add category breakdown
        if summary.expense_by_category:
            lines.append("")
            lines.append("📋 Expenses by Category:")
            lines.extend(Formatters.format_category_breakdown(summary.expense_by_category))
        
        return lines
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to specified length with suffix.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_number_with_commas(number: float) -> str:
        """
        Format number with comma separators.
        
        Args:
            number: Number to format
            
        Returns:
            Formatted number string
        """
        return f"{number:,.2f}" 