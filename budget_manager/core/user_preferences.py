"""
User Preferences Management for Smart Budget Manager
Handles storage and retrieval of user settings and preferences.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class Currency(Enum):
    """Supported currencies with their symbols and codes."""
    USD = {"code": "USD", "symbol": "$", "name": "US Dollar"}
    EUR = {"code": "EUR", "symbol": "€", "name": "Euro"}
    GBP = {"code": "GBP", "symbol": "£", "name": "British Pound"}
    JPY = {"code": "JPY", "symbol": "¥", "name": "Japanese Yen"}
    CAD = {"code": "CAD", "symbol": "C$", "name": "Canadian Dollar"}
    AUD = {"code": "AUD", "symbol": "A$", "name": "Australian Dollar"}
    CHF = {"code": "CHF", "symbol": "₣", "name": "Swiss Franc"}
    CNY = {"code": "CNY", "symbol": "¥", "name": "Chinese Yuan"}
    INR = {"code": "INR", "symbol": "₹", "name": "Indian Rupee"}
    BRL = {"code": "BRL", "symbol": "R$", "name": "Brazilian Real"}
    RUB = {"code": "RUB", "symbol": "₽", "name": "Russian Ruble"}
    KRW = {"code": "KRW", "symbol": "₩", "name": "South Korean Won"}
    MXN = {"code": "MXN", "symbol": "$", "name": "Mexican Peso"}
    ZAR = {"code": "ZAR", "symbol": "R", "name": "South African Rand"}
    SEK = {"code": "SEK", "symbol": "kr", "name": "Swedish Krona"}
    NOK = {"code": "NOK", "symbol": "kr", "name": "Norwegian Krone"}
    DKK = {"code": "DKK", "symbol": "kr", "name": "Danish Krone"}
    PLN = {"code": "PLN", "symbol": "zł", "name": "Polish Złoty"}
    TRY = {"code": "TRY", "symbol": "₺", "name": "Turkish Lira"}
    TND = {"code": "TND", "symbol": "د.ت", "name": "Tunisian Dinar"}
    NZD = {"code": "NZD", "symbol": "NZ$", "name": "New Zealand Dollar"}


class UserPreferences:
    """Manages user preferences and settings."""
    
    def __init__(self, preferences_file: Optional[str] = None):
        """
        Initialize user preferences manager.
        
        Args:
            preferences_file: Custom path to preferences file. If None, uses default.
        """
        if preferences_file is None:
            # Try to use user's home directory, fall back to current directory for deployment
            try:
                import os
                if os.environ.get('STREAMLIT_CLOUD_DEPLOYMENT'):
                    # For Streamlit Cloud deployment, use current directory
                    data_dir = Path("./data")
                else:
                    # For local development, use home directory
                    data_dir = Path.home() / ".budget_manager"
                
                data_dir.mkdir(exist_ok=True)
                preferences_file = str(data_dir / "preferences.json")
            except (PermissionError, OSError):
                # Fallback to current directory if home directory isn't accessible
                data_dir = Path("./data")
                data_dir.mkdir(exist_ok=True)
                preferences_file = str(data_dir / "preferences.json")
        
        self.preferences_file = preferences_file
        self._preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file or return defaults."""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load preferences ({e}). Using defaults.")
        
        # Return default preferences
        return {
            "currency": "USD",
            "savings_target_day": 3,
            "date_format": "%Y-%m-%d",
            "theme": "default",
            "decimal_places": 2,
            "show_cents": True,
            "group_thousands": True
        }
    
    def _save_preferences(self) -> None:
        """Save preferences to file."""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self._preferences, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save preferences ({e})")
    
    def get_currency(self) -> Currency:
        """Get the user's selected currency."""
        currency_code = self._preferences.get("currency", "USD")
        try:
            return Currency[currency_code]
        except KeyError:
            # Fallback to USD if invalid currency
            self.set_currency(Currency.USD)
            return Currency.USD
    
    def set_currency(self, currency: Currency) -> None:
        """Set the user's currency preference."""
        self._preferences["currency"] = currency.name
        self._save_preferences()
    
    def get_currency_symbol(self) -> str:
        """Get the symbol for the current currency."""
        return self.get_currency().value["symbol"]
    
    def get_currency_code(self) -> str:
        """Get the code for the current currency."""
        return self.get_currency().value["code"]
    
    def get_currency_name(self) -> str:
        """Get the name for the current currency."""
        return self.get_currency().value["name"]
    
    def get_savings_target_day(self) -> int:
        """Get the day of month for savings target."""
        return self._preferences.get("savings_target_day", 3)
    
    def set_savings_target_day(self, day: int) -> None:
        """Set the day of month for savings target."""
        if 1 <= day <= 28:
            self._preferences["savings_target_day"] = day
            self._save_preferences()
        else:
            raise ValueError("Target day must be between 1 and 28")
    
    def get_decimal_places(self) -> int:
        """Get number of decimal places for currency display."""
        return self._preferences.get("decimal_places", 2)
    
    def set_decimal_places(self, places: int) -> None:
        """Set number of decimal places for currency display."""
        if 0 <= places <= 4:
            self._preferences["decimal_places"] = places
            self._save_preferences()
        else:
            raise ValueError("Decimal places must be between 0 and 4")
    
    def get_show_cents(self) -> bool:
        """Whether to show cents in currency display."""
        return self._preferences.get("show_cents", True)
    
    def set_show_cents(self, show: bool) -> None:
        """Set whether to show cents in currency display."""
        self._preferences["show_cents"] = show
        self._save_preferences()
    
    def get_group_thousands(self) -> bool:
        """Whether to group thousands with commas."""
        return self._preferences.get("group_thousands", True)
    
    def set_group_thousands(self, group: bool) -> None:
        """Set whether to group thousands with commas."""
        self._preferences["group_thousands"] = group
        self._save_preferences()
    
    def get_theme(self) -> str:
        """Get the UI theme preference."""
        return self._preferences.get("theme", "default")
    
    def set_theme(self, theme: str) -> None:
        """Set the UI theme preference."""
        self._preferences["theme"] = theme
        self._save_preferences()
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences as a dictionary."""
        return self._preferences.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all preferences to defaults."""
        self._preferences = {
            "currency": "USD",
            "savings_target_day": 3,
            "date_format": "%Y-%m-%d",
            "theme": "default",
            "decimal_places": 2,
            "show_cents": True,
            "group_thousands": True
        }
        self._save_preferences()
    
    @staticmethod
    def get_available_currencies() -> Dict[str, Dict[str, str]]:
        """Get all available currencies."""
        return {currency.name: currency.value for currency in Currency}
    
    @staticmethod
    def get_currency_choices() -> list:
        """Get currency choices formatted for UI display."""
        choices = []
        for currency in Currency:
            info = currency.value
            choices.append(f"{info['code']} ({info['symbol']}) - {info['name']}")
        return choices


# Global preferences instance
_preferences_instance = None


def get_user_preferences() -> UserPreferences:
    """Get the global user preferences instance."""
    global _preferences_instance
    if _preferences_instance is None:
        _preferences_instance = UserPreferences()
    return _preferences_instance


def reset_preferences_instance():
    """Reset the global preferences instance (useful for testing)."""
    global _preferences_instance
    _preferences_instance = None 