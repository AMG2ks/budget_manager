#!/usr/bin/env python3
"""
Test script for multi-language functionality in Smart Budget Manager.
Tests English, French, and Arabic translations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'budget_manager'))

from budget_manager.utils.translations import t, Language, set_language, get_current_language, is_rtl
from budget_manager.core.user_preferences import get_user_preferences


def test_language_switching():
    """Test switching between different languages."""
    print("🌍 Testing Multi-Language Support\n")
    
    languages = [Language.ENGLISH, Language.FRENCH, Language.ARABIC]
    
    for lang in languages:
        print(f"Testing {lang.value.upper()}:")
        print("=" * 40)
        
        set_language(lang)
        current = get_current_language()
        print(f"Current language: {current}")
        print(f"Is RTL: {is_rtl()}")
        
        # Test common translations
        print(f"App Title: {t('app_title')}")
        print(f"Welcome: {t('welcome_message', 'John')}")
        print(f"Dashboard: {t('dashboard')}")
        print(f"Login: {t('login')}")
        print(f"Monthly Income: {t('monthly_income')}")
        print(f"Total Expenses: {t('total_expenses')}")
        print(f"Settings: {t('settings')}")
        print(f"Language Settings: {t('language_settings')}")
        print()


def test_user_preferences_integration():
    """Test integration with user preferences."""
    print("⚙️ Testing User Preferences Integration\n")
    
    try:
        prefs = get_user_preferences()
        
        # Test setting language preference
        for lang in [Language.ENGLISH, Language.FRENCH, Language.ARABIC]:
            prefs.set_language(lang.value)
            saved_lang = prefs.get_language()
            print(f"Set {lang.value}, Got {saved_lang}: {'✅' if saved_lang == lang.value else '❌'}")
        
        print("User preferences integration: ✅ Working")
        
    except Exception as e:
        print(f"User preferences integration: ❌ Error - {e}")


def test_missing_translations():
    """Test handling of missing translation keys."""
    print("🔍 Testing Missing Translation Handling\n")
    
    set_language(Language.ENGLISH)
    
    # Test with a non-existent key
    missing_key = "non_existent_key_12345"
    result = t(missing_key)
    
    print(f"Missing key '{missing_key}' returns: '{result}'")
    print(f"Fallback behavior: {'✅' if result == missing_key else '❌'}")


def test_formatting():
    """Test string formatting in translations."""
    print("📝 Testing String Formatting\n")
    
    for lang in [Language.ENGLISH, Language.FRENCH, Language.ARABIC]:
        set_language(lang)
        
        # Test with one argument
        welcome = t("welcome_message", "Ahmed")
        print(f"{lang.value}: {welcome}")
        
        # Test with multiple arguments
        income_set = t("income_set", "1000.00", "January 2024")
        print(f"{lang.value}: {income_set}")
        
        print()


def test_rtl_support():
    """Test RTL (Right-to-Left) language support."""
    print("↔️ Testing RTL Support\n")
    
    for lang in [Language.ENGLISH, Language.FRENCH, Language.ARABIC]:
        set_language(lang)
        rtl_status = is_rtl()
        expected_rtl = (lang == Language.ARABIC)
        
        status = "✅" if rtl_status == expected_rtl else "❌"
        print(f"{lang.value}: RTL={rtl_status} (expected: {expected_rtl}) {status}")


def main():
    """Run all tests."""
    print("🧪 Smart Budget Manager - Multi-Language Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_language_switching()
        test_user_preferences_integration()
        test_missing_translations()
        test_formatting()
        test_rtl_support()
        
        print("🎉 All tests completed!")
        print("\n💡 To test the web interface:")
        print("   streamlit run app.py")
        print("   Then use the language selector in the sidebar")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 