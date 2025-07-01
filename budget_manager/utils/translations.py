"""
Internationalization (i18n) system for Smart Budget Manager.
Supports English, French, and Arabic with RTL layout for Arabic.
"""

from typing import Dict, Any, Optional
from enum import Enum


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    FRENCH = "fr"
    ARABIC = "ar"


class TranslationManager:
    """Manages translations and language settings."""
    
    def __init__(self):
        """Initialize translation manager."""
        self.current_language = Language.ENGLISH
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_translations()
    
    def load_translations(self) -> None:
        """Load all translation files."""
        # English translations (base)
        self.translations[Language.ENGLISH] = {
            "app_title": "Smart Budget Manager",
            "welcome_message": "Welcome, {}!",
            "navigation": "Navigation",
            "logout": "Logout",
            "dashboard": "Dashboard",
            "income_goals": "Income & Goals",
            "expenses": "Expenses", 
            "reports": "Reports",
            "settings": "Settings",
            "login": "Login",
            "register": "Register",
            "username": "Username",
            "password": "Password",
            "email": "Email",
            "full_name": "Full Name",
            "login_to_account": "Login to Your Account",
            "create_account": "Create New Account",
            "login_button": "🚀 Login",
            "register_button": "✨ Create Account",
            "choose_option": "Choose an option:",
            "enter_username": "Enter your username",
            "enter_password": "Enter your password",
            "your_email": "your.email@example.com",
            "full_name_optional": "Your full name (optional)",
            "choose_username": "Choose a username",
            "choose_password": "Choose a strong password",
            "confirm_password": "Confirm Password",
            "confirm_your_password": "Confirm your password",
            "welcome_back": "Welcome back, {}! 🎉",
            "account_created": "Account created successfully for {}! 🎉",
            "please_login": "Please login with your new credentials.",
            "login_failed": "Login failed: {}",
            "registration_failed": "Registration failed: {}",
            "fill_all_fields": "Please fill in all fields",
            "fill_required_fields": "Please fill in all required fields",
            "passwords_not_match": "Passwords do not match",
            "password_min_length": "Password must be at least 6 characters",
            "invalid_email": "Please enter a valid email address",
            "username_help": "Must be 3-50 characters, letters, numbers, hyphens and underscores only",
            "password_help": "Must be at least 6 characters",
            "error_occurred": "An error occurred: {}",
            "user_account": "User Account",
            "account_stats": "Account Stats:",
            "income_entries": "Income entries: {}",
            "total_expenses": "Expenses: {}",
            "total_goals": "Savings goals: {}",
            "member_since": "Member since: {} days",
            "language_settings": "Language Settings",
            "select_language": "Select Language",
            "language_english": "English",
            "language_french": "Français", 
            "language_arabic": "العربية",
            "language_changed": "Language changed to {}",
            "budget_dashboard": "Budget Dashboard",
            "monthly_income": "Monthly Income",
            "current_savings": "Current Savings",
            "savings_target": "Savings Target",
            "smart_recommendation": "Today's Smart Recommendation",
            "daily_spending_limit": "Daily Spending Limit:",
            "days_remaining": "Days Remaining:",
            "spent_this_month": "Spent This Month:",
            "projected_savings": "Projected Savings:",
            "savings_progress": "Savings Progress",
            "smart_alerts": "Smart Alerts",
            "recent_expenses": "Recent Expenses",
            "no_budget_data": "No budget data available. Please set up your income and savings goals first!",
            "set_income": "Set Income",
            "add_expense": "Add Expense",
            "error_loading_dashboard": "Error loading dashboard: {}",
            "set_monthly_income": "Set Monthly Income",
            "monthly_income_label": "Monthly Income",
            "description_optional": "Description (optional)",
            "eg_main_salary": "e.g., Main salary",
            "month": "Month",
            "set_income_button": "💰 Set Income",
            "current_month_income": "Current Month Income",
            "recent_entries": "Recent Entries:",
            "income_set": "Income set: {} for {}",
            "error_setting_income": "Error setting income: {}",
            "set_savings_goals": "Set Savings Goals",
            "monthly_savings_target": "Monthly Savings Target", 
            "goal_description_optional": "Goal Description (optional)",
            "eg_emergency_fund": "e.g., Emergency fund",
            "target_month": "Target Month",
            "set_goal_button": "🎯 Set Goal",
            "current_month_goal": "Current Month Goal",
            "description": "Description:",
            "savings_goal_set": "Savings goal set: {} for {}",
            "no_savings_goal": "No savings goal set for current month",
            "error_setting_goal": "Error setting goal: {}",
            "expense_management": "Expense Management",
            "add_expense_tab": "Add Expense",
            "view_expenses_tab": "View Expenses",
            "add_new_expense": "Add New Expense",
            "amount": "Amount",
            "category": "Category",
            "date": "Date",
            "add_expense_button": "💸 Add Expense",
            "expense_added": "Expense added: {} - {}",
            "updated_daily_limit": "Updated daily limit: {}",
            "today_spending": "Today's Spending",
            "today_expenses": "Today's Expenses:",
            "error_adding_expense": "Error adding expense: {}",
            "expense_history": "Expense History",
            "time_period": "Time Period",
            "category_filter": "Category Filter",
            "all_categories": "All",
            "number_of_records": "Number of Records",
            "total_amount": "Total Amount",
            "number_of_expenses": "Number of Expenses",
            "average_amount": "Average Amount",
            "spending_by_category": "Spending by Category (Last {} days)",
            "no_expenses_found": "No expenses found for the selected criteria.",
            "reports_analytics": "Reports & Analytics",
            "monthly_report": "Monthly Report",
            "trends": "Trends", 
            "goals_analysis": "Goals Analysis",
            "monthly_budget_report": "Monthly Budget Report",
            "select_month": "Select Month",
            "income": "Income",
            "expenses": "Expenses",
            "savings": "Savings",
            "savings_rate": "Savings Rate",
            "financial_summary": "Financial Summary",
            "goal_achievement": "Savings Goal Achievement",
            "expense_categories": "Expense Categories",
            "percentage": "Percentage",
            "category_distribution": "Category Distribution",
            "no_data_available": "No data available for {}",
            "error_generating_report": "Error generating report: {}",
            "spending_trends": "Spending Trends",
            "monthly_spending_trend": "Monthly Spending Trend",
            "monthly_transaction_count": "Monthly Transaction Count",
            "not_enough_data": "Not enough data to show trends. Start adding expenses to see trends over time!",
            "target_amount": "Target Amount",
            "progress": "Progress",
            "days_passed": "Days Passed",
            "on_track_goal": "You're on track to meet your savings goal!",
            "adjust_spending": "You may need to adjust your spending to meet your goal.",
            "required_daily_savings": "To reach your goal, you need to save {} per day for the remaining {} days.",
            "setup_goals": "Set up your income and savings goals to see goal analysis.",
            "application_settings": "Application Settings",
            "data_management": "Data Management",
            "preferences": "Preferences",
            "export_data": "Export Data",
            "export_expenses_csv": "📤 Export Expenses to CSV",
            "download_csv": "💾 Download CSV",
            "no_expenses_export": "No expenses to export",
            "error_exporting": "Error exporting data: {}",
            "database_info": "Database Info",
            "database_statistics": "Database Statistics:",
            "total_expenses_stat": "Total Expenses: {}",
            "income_entries_stat": "Income Entries: {}",
            "savings_goals_stat": "Savings Goals: {}",
            "error_loading_db_info": "Error loading database info: {}",
            "reset_database": "Reset Database",
            "danger_zone": "Danger Zone",
            "reset_warning": "This will permanently delete ALL your data:",
            "reset_warning_income": "Income entries",
            "reset_warning_expenses": "Expense records",
            "reset_warning_goals": "Savings goals", 
            "reset_warning_history": "All historical data",
            "understand_delete": "I understand this will delete all my data",
            "absolutely_sure": "I am absolutely sure I want to proceed",
            "reset_database_button": "🗑️ RESET DATABASE",
            "database_reset_success": "Database has been reset successfully! The page will refresh.",
            "database_reset_error": "Error resetting database: {}",
            "currency_settings": "Currency Settings",
            "select_currency": "Select Currency",
            "currency_preview": "Preview:",
            "formatting_options": "Formatting Options",
            "decimal_places": "Decimal Places",
            "thousands_separator": "Thousands Separator",
            "currency_updated": "Currency settings updated successfully!",
            "food": "Food",
            "transportation": "Transportation", 
            "entertainment": "Entertainment",
            "utilities": "Utilities",
            "shopping": "Shopping",
            "health": "Health",
            "education": "Education",
            "other": "Other",
            "save": "Save",
            "cancel": "Cancel",
            "close": "Close",
            "delete": "Delete",
            "edit": "Edit",
            "add": "Add",
            "update": "Update",
            "confirm": "Confirm",
            "success": "Success",
            "error": "Error",
            "warning": "Warning",
            "info": "Info",
            "loading": "Loading...",
            "no_data": "No data available",
            "required": "Required",
            "optional": "Optional"
        }
        
        # French translations
        self.translations[Language.FRENCH] = {
            "app_title": "Gestionnaire de Budget Intelligent",
            "welcome_message": "Bienvenue, {} !",
            "navigation": "Navigation",
            "logout": "Déconnexion",
            "dashboard": "Tableau de bord",
            "income_goals": "Revenus et Objectifs",
            "expenses": "Dépenses",
            "reports": "Rapports",
            "settings": "Paramètres",
            "login": "Connexion",
            "register": "S'inscrire",
            "username": "Nom d'utilisateur",
            "password": "Mot de passe",
            "email": "E-mail",
            "full_name": "Nom complet",
            "login_to_account": "Connectez-vous à votre compte",
            "create_account": "Créer un nouveau compte",
            "login_button": "🚀 Se connecter",
            "register_button": "✨ Créer un compte",
            "choose_option": "Choisissez une option :",
            "enter_username": "Entrez votre nom d'utilisateur",
            "enter_password": "Entrez votre mot de passe",
            "your_email": "votre.email@exemple.com",
            "full_name_optional": "Votre nom complet (optionnel)",
            "choose_username": "Choisissez un nom d'utilisateur",
            "choose_password": "Choisissez un mot de passe fort",
            "confirm_password": "Confirmer le mot de passe",
            "confirm_your_password": "Confirmez votre mot de passe",
            "welcome_back": "Bon retour, {} ! 🎉",
            "account_created": "Compte créé avec succès pour {} ! 🎉",
            "please_login": "Veuillez vous connecter avec vos nouveaux identifiants.",
            "login_failed": "Échec de la connexion : {}",
            "registration_failed": "Échec de l'inscription : {}",
            "fill_all_fields": "Veuillez remplir tous les champs",
            "fill_required_fields": "Veuillez remplir tous les champs obligatoires",
            "passwords_not_match": "Les mots de passe ne correspondent pas",
            "password_min_length": "Le mot de passe doit contenir au moins 6 caractères",
            "invalid_email": "Veuillez entrer une adresse e-mail valide",
            "username_help": "Doit contenir 3-50 caractères, lettres, chiffres, tirets et underscores uniquement",
            "password_help": "Doit contenir au moins 6 caractères",
            "error_occurred": "Une erreur s'est produite : {}",
            "user_account": "Compte utilisateur",
            "account_stats": "Statistiques du compte :",
            "income_entries": "Entrées de revenus : {}",
            "total_expenses": "Dépenses : {}",
            "total_goals": "Objectifs d'épargne : {}",
            "member_since": "Membre depuis : {} jours",
            "language_settings": "Paramètres de langue",
            "select_language": "Sélectionner la langue",
            "language_english": "English",
            "language_french": "Français",
            "language_arabic": "العربية",
            "language_changed": "Langue changée en {}",
            "budget_dashboard": "Tableau de bord du budget",
            "monthly_income": "Revenus mensuels",
            "current_savings": "Épargne actuelle",
            "savings_target": "Objectif d'épargne",
            "smart_recommendation": "Recommandation intelligente d'aujourd'hui",
            "daily_spending_limit": "Limite de dépense quotidienne :",
            "days_remaining": "Jours restants :",
            "spent_this_month": "Dépensé ce mois :",
            "projected_savings": "Épargne projetée :",
            "savings_progress": "Progrès de l'épargne",
            "smart_alerts": "Alertes intelligentes",
            "recent_expenses": "Dépenses récentes",
            "no_budget_data": "Aucune donnée budgétaire disponible. Veuillez d'abord configurer vos revenus et objectifs d'épargne !",
            "set_income": "Définir les revenus",
            "add_expense": "Ajouter une dépense",
            "error_loading_dashboard": "Erreur lors du chargement du tableau de bord : {}",
            "set_monthly_income": "Définir les revenus mensuels",
            "monthly_income_label": "Revenus mensuels",
            "description_optional": "Description (optionnelle)",
            "eg_main_salary": "ex. Salaire principal",
            "month": "Mois",
            "set_income_button": "💰 Définir les revenus",
            "current_month_income": "Revenus du mois actuel",
            "recent_entries": "Entrées récentes :",
            "income_set": "Revenus définis : {} pour {}",
            "error_setting_income": "Erreur lors de la définition des revenus : {}",
            "set_savings_goals": "Définir les objectifs d'épargne",
            "monthly_savings_target": "Objectif d'épargne mensuel",
            "goal_description_optional": "Description de l'objectif (optionnelle)",
            "eg_emergency_fund": "ex. Fonds d'urgence",
            "target_month": "Mois cible",
            "set_goal_button": "🎯 Définir l'objectif",
            "current_month_goal": "Objectif du mois actuel",
            "description": "Description :",
            "savings_goal_set": "Objectif d'épargne défini : {} pour {}",
            "no_savings_goal": "Aucun objectif d'épargne défini pour le mois actuel",
            "error_setting_goal": "Erreur lors de la définition de l'objectif : {}",
            "expense_management": "Gestion des dépenses",
            "add_expense_tab": "Ajouter une dépense",
            "view_expenses_tab": "Voir les dépenses",
            "add_new_expense": "Ajouter une nouvelle dépense",
            "amount": "Montant",
            "category": "Catégorie",
            "date": "Date",
            "add_expense_button": "💸 Ajouter une dépense",
            "expense_added": "Dépense ajoutée : {} - {}",
            "updated_daily_limit": "Limite quotidienne mise à jour : {}",
            "today_spending": "Dépenses d'aujourd'hui",
            "today_expenses": "Dépenses d'aujourd'hui :",
            "error_adding_expense": "Erreur lors de l'ajout de la dépense : {}",
            "expense_history": "Historique des dépenses",
            "time_period": "Période",
            "category_filter": "Filtre par catégorie",
            "all_categories": "Toutes",
            "number_of_records": "Nombre d'enregistrements",
            "total_amount": "Montant total",
            "number_of_expenses": "Nombre de dépenses",
            "average_amount": "Montant moyen",
            "spending_by_category": "Dépenses par catégorie (Derniers {} jours)",
            "no_expenses_found": "Aucune dépense trouvée pour les critères sélectionnés.",
            "reports_analytics": "Rapports et analyses",
            "monthly_report": "Rapport mensuel",
            "trends": "Tendances",
            "goals_analysis": "Analyse des objectifs",
            "monthly_budget_report": "Rapport budgétaire mensuel",
            "select_month": "Sélectionner le mois",
            "income": "Revenus",
            "expenses": "Dépenses",
            "savings": "Épargne",
            "savings_rate": "Taux d'épargne",
            "financial_summary": "Résumé financier",
            "goal_achievement": "Réalisation de l'objectif d'épargne",
            "expense_categories": "Catégories de dépenses",
            "percentage": "Pourcentage",
            "category_distribution": "Répartition par catégorie",
            "no_data_available": "Aucune donnée disponible pour {}",
            "error_generating_report": "Erreur lors de la génération du rapport : {}",
            "spending_trends": "Tendances des dépenses",
            "monthly_spending_trend": "Tendance des dépenses mensuelles",
            "monthly_transaction_count": "Nombre de transactions mensuelles",
            "not_enough_data": "Pas assez de données pour afficher les tendances. Commencez à ajouter des dépenses pour voir les tendances au fil du temps !",
            "target_amount": "Montant cible",
            "progress": "Progrès",
            "days_passed": "Jours écoulés",
            "on_track_goal": "Vous êtes en bonne voie pour atteindre votre objectif d'épargne !",
            "adjust_spending": "Vous devrez peut-être ajuster vos dépenses pour atteindre votre objectif.",
            "required_daily_savings": "Pour atteindre votre objectif, vous devez économiser {} par jour pendant les {} jours restants.",
            "setup_goals": "Configurez vos revenus et objectifs d'épargne pour voir l'analyse des objectifs.",
            "application_settings": "Paramètres de l'application",
            "data_management": "Gestion des données",
            "preferences": "Préférences",
            "export_data": "Exporter les données",
            "export_expenses_csv": "📤 Exporter les dépenses en CSV",
            "download_csv": "💾 Télécharger CSV",
            "no_expenses_export": "Aucune dépense à exporter",
            "error_exporting": "Erreur lors de l'exportation des données : {}",
            "database_info": "Informations de la base de données",
            "database_statistics": "Statistiques de la base de données :",
            "total_expenses_stat": "Total des dépenses : {}",
            "income_entries_stat": "Entrées de revenus : {}",
            "savings_goals_stat": "Objectifs d'épargne : {}",
            "error_loading_db_info": "Erreur lors du chargement des informations de la base de données : {}",
            "reset_database": "Réinitialiser la base de données",
            "danger_zone": "Zone de danger",
            "reset_warning": "Ceci supprimera définitivement TOUTES vos données :",
            "reset_warning_income": "Entrées de revenus",
            "reset_warning_expenses": "Enregistrements de dépenses",
            "reset_warning_goals": "Objectifs d'épargne",
            "reset_warning_history": "Toutes les données historiques",
            "understand_delete": "Je comprends que cela supprimera toutes mes données",
            "absolutely_sure": "Je suis absolument sûr de vouloir procéder",
            "reset_database_button": "🗑️ RÉINITIALISER LA BASE DE DONNÉES",
            "database_reset_success": "La base de données a été réinitialisée avec succès ! La page va se rafraîchir.",
            "database_reset_error": "Erreur lors de la réinitialisation de la base de données : {}",
            "currency_settings": "Paramètres de devise",
            "select_currency": "Sélectionner la devise",
            "currency_preview": "Aperçu :",
            "formatting_options": "Options de formatage",
            "decimal_places": "Décimales",
            "thousands_separator": "Séparateur de milliers",
            "currency_updated": "Paramètres de devise mis à jour avec succès !",
            "food": "Nourriture",
            "transportation": "Transport",
            "entertainment": "Divertissement",
            "utilities": "Services publics",
            "shopping": "Shopping",
            "health": "Santé",
            "education": "Éducation",
            "other": "Autre",
            "save": "Enregistrer",
            "cancel": "Annuler",
            "close": "Fermer",
            "delete": "Supprimer",
            "edit": "Modifier",
            "add": "Ajouter",
            "update": "Mettre à jour",
            "confirm": "Confirmer",
            "success": "Succès",
            "error": "Erreur",
            "warning": "Avertissement",
            "info": "Information",
            "loading": "Chargement...",
            "no_data": "Aucune donnée disponible",
            "required": "Obligatoire",
            "optional": "Optionnel"
        }
        
        # Arabic translations
        self.translations[Language.ARABIC] = {
            "app_title": "مدير الميزانية الذكي",
            "welcome_message": "مرحباً، {}!",
            "navigation": "التنقل",
            "logout": "تسجيل الخروج",
            "dashboard": "لوحة التحكم",
            "income_goals": "الدخل والأهداف",
            "expenses": "المصروفات",
            "reports": "التقارير",
            "settings": "الإعدادات",
            "login": "تسجيل الدخول",
            "register": "تسجيل",
            "username": "اسم المستخدم",
            "password": "كلمة المرور",
            "email": "البريد الإلكتروني",
            "full_name": "الاسم الكامل",
            "login_to_account": "تسجيل الدخول إلى حسابك",
            "create_account": "إنشاء حساب جديد",
            "login_button": "🚀 تسجيل الدخول",
            "register_button": "✨ إنشاء حساب",
            "choose_option": "اختر خياراً:",
            "enter_username": "أدخل اسم المستخدم",
            "enter_password": "أدخل كلمة المرور",
            "your_email": "بريدك.الالكتروني@مثال.com",
            "full_name_optional": "اسمك الكامل (اختياري)",
            "choose_username": "اختر اسم مستخدم",
            "choose_password": "اختر كلمة مرور قوية",
            "confirm_password": "تأكيد كلمة المرور",
            "confirm_your_password": "أكد كلمة المرور",
            "welcome_back": "مرحباً بعودتك، {}! 🎉",
            "account_created": "تم إنشاء الحساب بنجاح لـ {}! 🎉",
            "please_login": "يرجى تسجيل الدخول باستخدام بياناتك الجديدة.",
            "login_failed": "فشل تسجيل الدخول: {}",
            "registration_failed": "فشل التسجيل: {}",
            "fill_all_fields": "يرجى ملء جميع الحقول",
            "fill_required_fields": "يرجى ملء جميع الحقول المطلوبة",
            "passwords_not_match": "كلمات المرور غير متطابقة",
            "password_min_length": "يجب أن تكون كلمة المرور 6 أحرف على الأقل",
            "invalid_email": "يرجى إدخال عنوان بريد إلكتروني صحيح",
            "username_help": "يجب أن يكون 3-50 حرفاً، أحرف وأرقام وشرطات وشرطات سفلية فقط",
            "password_help": "يجب أن تكون 6 أحرف على الأقل",
            "error_occurred": "حدث خطأ: {}",
            "user_account": "حساب المستخدم",
            "language_settings": "إعدادات اللغة",
            "select_language": "اختر اللغة",
            "language_english": "English",
            "language_french": "Français",
            "language_arabic": "العربية",
            "language_changed": "تم تغيير اللغة إلى {}",
            "budget_dashboard": "لوحة تحكم الميزانية",
            "monthly_income": "الدخل الشهري",
            "total_expenses": "إجمالي المصروفات",
            "current_savings": "المدخرات الحالية",
            "savings_target": "هدف الادخار",
            "set_monthly_income": "تحديد الدخل الشهري",
            "add_new_expense": "إضافة مصروف جديد",
            "amount": "المبلغ",
            "description": "الوصف",
            "category": "الفئة",
            "save": "حفظ",
            "cancel": "إلغاء",
            "error": "خطأ",
            "success": "نجح"
        }
    
    def set_language(self, language: Language) -> None:
        """Set current language."""
        self.current_language = language
    
    def get_language(self) -> Language:
        """Get current language."""
        return self.current_language
    
    def is_rtl(self) -> bool:
        """Check if current language is right-to-left."""
        return self.current_language == Language.ARABIC
    
    def translate(self, key: str, *args) -> str:
        """
        Get translated text for the given key.
        
        Args:
            key: Translation key
            *args: Format arguments
            
        Returns:
            Translated text
        """
        translations = self.translations.get(self.current_language, {})
        text = translations.get(key, key)  # Fallback to key if not found
        
        # Format with arguments if provided
        if args:
            try:
                return text.format(*args)
            except (ValueError, IndexError):
                return text
        
        return text
    
    def get_language_options(self) -> Dict[str, str]:
        """Get available language options."""
        return {
            Language.ENGLISH: self.translate("language_english"),
            Language.FRENCH: self.translate("language_french"), 
            Language.ARABIC: self.translate("language_arabic")
        }


# Global translation manager instance
_translation_manager = TranslationManager()


def get_translation_manager() -> TranslationManager:
    """Get the global translation manager instance."""
    return _translation_manager


def t(key: str, *args) -> str:
    """
    Shorthand function for translation.
    
    Args:
        key: Translation key
        *args: Format arguments
        
    Returns:
        Translated text
    """
    return _translation_manager.translate(key, *args)


def set_language(language: Language) -> None:
    """Set the application language."""
    _translation_manager.set_language(language)


def get_current_language() -> Language:
    """Get the current application language."""
    return _translation_manager.get_language()


def is_rtl() -> bool:
    """Check if current language requires right-to-left layout."""
    return _translation_manager.is_rtl() 