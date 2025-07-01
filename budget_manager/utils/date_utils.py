"""
Date utility functions for the budget manager.
"""

from datetime import date, datetime, timedelta
from typing import Tuple
from calendar import monthrange


class DateUtils:
    """Utility class for date operations."""
    
    @staticmethod
    def get_month_boundaries(target_date: date) -> Tuple[date, date]:
        """
        Get the first and last day of the month for a given date.
        
        Args:
            target_date: Date to get month boundaries for
            
        Returns:
            Tuple of (first_day, last_day) of the month
        """
        first_day = target_date.replace(day=1)
        last_day_num = monthrange(target_date.year, target_date.month)[1]
        last_day = target_date.replace(day=last_day_num)
        return first_day, last_day
    
    @staticmethod
    def get_days_in_month(target_date: date) -> int:
        """
        Get the number of days in the month for a given date.
        
        Args:
            target_date: Date to get days count for
            
        Returns:
            Number of days in the month
        """
        return monthrange(target_date.year, target_date.month)[1]
    
    @staticmethod
    def get_days_remaining_in_month(target_date: date = None) -> int:
        """
        Get the number of days remaining in the month.
        
        Args:
            target_date: Date to calculate from (default: today)
            
        Returns:
            Number of days remaining in the month
        """
        if target_date is None:
            target_date = date.today()
        
        days_in_month = DateUtils.get_days_in_month(target_date)
        return days_in_month - target_date.day
    
    @staticmethod
    def get_next_month_start(target_date: date = None) -> date:
        """
        Get the first day of the next month.
        
        Args:
            target_date: Date to calculate from (default: today)
            
        Returns:
            First day of the next month
        """
        if target_date is None:
            target_date = date.today()
        
        if target_date.month == 12:
            return date(target_date.year + 1, 1, 1)
        else:
            return date(target_date.year, target_date.month + 1, 1)
    
    @staticmethod
    def get_previous_month_start(target_date: date = None) -> date:
        """
        Get the first day of the previous month.
        
        Args:
            target_date: Date to calculate from (default: today)
            
        Returns:
            First day of the previous month
        """
        if target_date is None:
            target_date = date.today()
        
        if target_date.month == 1:
            return date(target_date.year - 1, 12, 1)
        else:
            return date(target_date.year, target_date.month - 1, 1)
    
    @staticmethod
    def get_target_date(day: int = 3, month: date = None) -> date:
        """
        Get target date (default: 3rd of next month).
        
        Args:
            day: Day of the month for target
            month: Month to calculate from (default: current month)
            
        Returns:
            Target date
        """
        if month is None:
            month = date.today()
        
        next_month = DateUtils.get_next_month_start(month)
        try:
            return next_month.replace(day=day)
        except ValueError:
            # Handle case where day doesn't exist in month (e.g., Feb 30)
            days_in_month = DateUtils.get_days_in_month(next_month)
            return next_month.replace(day=min(day, days_in_month))
    
    @staticmethod
    def parse_date_string(date_str: str) -> date:
        """
        Parse date string in various formats.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            Parsed date object
            
        Raises:
            ValueError: If date string cannot be parsed
        """
        # Common date formats to try
        formats = [
            "%Y-%m-%d",    # 2023-12-25
            "%m/%d/%Y",    # 12/25/2023
            "%d/%m/%Y",    # 25/12/2023
            "%m-%d-%Y",    # 12-25-2023
            "%d-%m-%Y",    # 25-12-2023
            "%Y/%m/%d",    # 2023/12/25
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date string: {date_str}")
    
    @staticmethod
    def format_date_display(target_date: date) -> str:
        """
        Format date for display purposes.
        
        Args:
            target_date: Date to format
            
        Returns:
            Formatted date string
        """
        return target_date.strftime("%B %d, %Y")
    
    @staticmethod
    def format_month_year(target_date: date) -> str:
        """
        Format date as month and year only.
        
        Args:
            target_date: Date to format
            
        Returns:
            Formatted month and year string
        """
        return target_date.strftime("%B %Y")
    
    @staticmethod
    def get_date_range_for_period(period: str, reference_date: date = None) -> Tuple[date, date]:
        """
        Get date range for various periods.
        
        Args:
            period: Period type ('today', 'week', 'month', 'year')
            reference_date: Reference date (default: today)
            
        Returns:
            Tuple of (start_date, end_date)
            
        Raises:
            ValueError: If period is not recognized
        """
        if reference_date is None:
            reference_date = date.today()
        
        if period == 'today':
            return reference_date, reference_date
        
        elif period == 'week':
            # Get Monday to Sunday of current week
            days_since_monday = reference_date.weekday()
            start_date = reference_date - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=6)
            return start_date, end_date
        
        elif period == 'month':
            return DateUtils.get_month_boundaries(reference_date)
        
        elif period == 'year':
            start_date = date(reference_date.year, 1, 1)
            end_date = date(reference_date.year, 12, 31)
            return start_date, end_date
        
        else:
            raise ValueError(f"Unknown period: {period}")
    
    @staticmethod
    def is_same_month(date1: date, date2: date) -> bool:
        """
        Check if two dates are in the same month and year.
        
        Args:
            date1: First date
            date2: Second date
            
        Returns:
            True if dates are in the same month
        """
        return date1.year == date2.year and date1.month == date2.month 