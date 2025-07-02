"""
Authentication UI components for the Streamlit multi-user budget manager.
"""

import streamlit as st
from typing import Optional, Dict, Any

from budget_manager.services.auth_service import AuthService, AuthenticationError
from budget_manager.core.models import UserCreate, UserLogin, UserProfile
from budget_manager.utils.translations import t, Language, set_language, get_current_language, is_rtl
from budget_manager.core.user_preferences import get_user_preferences


class AuthUI:
    """Authentication UI handler for Streamlit."""
    
    def __init__(self):
        """Initialize authentication UI."""
        self.auth_service = AuthService()
        
        # Initialize session state for authentication
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'auth_mode' not in st.session_state:
            st.session_state.auth_mode = 'login'  # 'login' or 'register'
        
        # Initialize language from preferences
        if 'language_initialized' not in st.session_state:
            try:
                prefs = get_user_preferences()
                lang_code = prefs.get_language()
                language = Language(lang_code)
                set_language(language)
                st.session_state.language_initialized = True
            except:
                set_language(Language.ENGLISH)
                st.session_state.language_initialized = True
    
    def render_language_selector(self):
        """Render language selector in sidebar."""
        with st.sidebar:
            st.markdown("---")
            
            current_lang = get_current_language()
            language_options = {
                Language.ENGLISH: "🇺🇸 English",
                Language.FRENCH: "🇫🇷 Français",
                Language.ARABIC: "🇸🇦 العربية"
            }
            
            selected_lang = st.selectbox(
                t("select_language"),
                options=list(language_options.keys()),
                format_func=lambda x: language_options[x],
                index=list(language_options.keys()).index(current_lang),
                key="language_selector"
            )
            
            if selected_lang != current_lang:
                set_language(selected_lang)
                # Save to preferences
                try:
                    prefs = get_user_preferences()
                    prefs.set_language(selected_lang.value)
                except:
                    pass
                st.rerun()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return st.session_state.authenticated and st.session_state.user is not None
    
    def get_current_user(self) -> Optional[UserProfile]:
        """Get current authenticated user."""
        if self.is_authenticated():
            return st.session_state.user
        return None
    
    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID."""
        user = self.get_current_user()
        return user.id if user else None
    
    def logout(self):
        """Logout current user."""
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.auth_mode = 'login'
        st.rerun()
    
    def render_auth_form(self) -> bool:
        """
        Render authentication form.
        
        Returns:
            True if user is authenticated, False otherwise
        """
        if self.is_authenticated():
            return True
        
        # Set page config for RTL support
        if is_rtl():
            st.markdown("""
            <style>
            .main .block-container {
                direction: rtl;
                text-align: right;
            }
            .stRadio > label {
                direction: rtl;
                text-align: right;
            }
            .stTextInput > label {
                direction: rtl;
                text-align: right;
            }
            .stButton > button {
                direction: rtl;
            }
            .stForm {
                direction: rtl;
                text-align: right;
            }
            .stMarkdown {
                direction: rtl;
                text-align: right;
            }
            .stSelectbox > label {
                direction: rtl;
                text-align: right;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Main authentication container
        st.markdown(f"## 🏦 {t('app_title')}")
        st.markdown("---")
        
        # Language selector
        self.render_language_selector()
        
        # Tab selection
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            auth_tab = st.radio(
                t("choose_option"),
                [t("login"), t("register"), "🔄 Reset Password"],
                key="auth_tab",
                horizontal=True
            )
        
        if auth_tab == t("login"):
            return self._render_login_form()
        elif auth_tab == t("register"):
            return self._render_register_form()
        else:
            return self._render_reset_password_form()
    
    def _render_login_form(self) -> bool:
        """Render login form."""
        with st.container():
            st.markdown(f"### 🔐 {t('login_to_account')}")
            
            with st.form("login_form"):
                username = st.text_input(
                    t("username"),
                    placeholder=t("enter_username"),
                    help=t("username_help")
                )
                password = st.text_input(
                    t("password"),
                    type="password",
                    placeholder=t("enter_password")
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    login_button = st.form_submit_button(t("login_button"), use_container_width=True)
                
                if login_button:
                    if not username or not password:
                        st.error(t("fill_all_fields"))
                        return False
                    
                    try:
                        login_data = UserLogin(username=username, password=password)
                        user = self.auth_service.login_user(login_data)
                        
                        # Set session state
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        
                        st.success(t("welcome_back", user.full_name or user.username))
                        st.rerun()
                        
                    except AuthenticationError as e:
                        st.error(t("login_failed", str(e)))
                    except Exception as e:
                        st.error(t("error_occurred", str(e)))
            
            # Forgot password link (outside form)
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Forgot Password?", use_container_width=True, type="secondary"):
                    # Switch to reset password tab
                    st.session_state.auth_tab = "🔄 Reset Password"
                    st.rerun()
        
        return False
    
    def _render_register_form(self) -> bool:
        """Render registration form."""
        with st.container():
            st.markdown(f"### 📝 {t('create_account')}")
            
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    username = st.text_input(
                        f"{t('username')} *",
                        placeholder=t("choose_username"),
                        help=t("username_help")
                    )
                    email = st.text_input(
                        f"{t('email')} *",
                        placeholder=t("your_email"),
                        help=t("invalid_email")
                    )
                
                with col2:
                    full_name = st.text_input(
                        t("full_name"),
                        placeholder=t("full_name_optional")
                    )
                    password = st.text_input(
                        f"{t('password')} *",
                        type="password",
                        placeholder=t("choose_password"),
                        help=t("password_help")
                    )
                
                confirm_password = st.text_input(
                    f"{t('confirm_password')} *",
                    type="password",
                    placeholder=t("confirm_your_password")
                )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    register_button = st.form_submit_button(t("register_button"), use_container_width=True)
                
                if register_button:
                    # Validation
                    errors = []
                    
                    if not username or not email or not password or not confirm_password:
                        errors.append(t("fill_required_fields"))
                    
                    if password != confirm_password:
                        errors.append(t("passwords_not_match"))
                    
                    if len(password) < 6:
                        errors.append(t("password_min_length"))
                    
                    if "@" not in email or "." not in email:
                        errors.append(t("invalid_email"))
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                        return False
                    
                    try:
                        user_data = UserCreate(
                            username=username,
                            email=email,
                            password=password,
                            full_name=full_name if full_name else None
                        )
                        
                        user = self.auth_service.register_user(user_data)
                        
                        st.success(t("account_created", user.username))
                        st.info(t("please_login"))
                        
                        # Switch to login mode
                        st.session_state.auth_mode = 'login'
                        st.rerun()
                        
                    except AuthenticationError as e:
                        st.error(t("registration_failed", str(e)))
                    except Exception as e:
                        st.error(t("error_occurred", str(e)))
        
        return False
    
    def _render_reset_password_form(self) -> bool:
        """Render password reset form."""
        with st.container():
            st.markdown(f"### 🔄 Reset Password")
            st.info("💡 Enter your username and email to reset your password.")
            
            with st.form("reset_password_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    username = st.text_input(
                        "Username *",
                        placeholder="Enter your username",
                        help="The username you use to login"
                    )
                    email = st.text_input(
                        "Email *",
                        placeholder="Enter your email address",
                        help="Email associated with your account"
                    )
                
                with col2:
                    new_password = st.text_input(
                        "New Password *",
                        type="password",
                        placeholder="Enter new password",
                        help="Choose a strong password (minimum 6 characters)"
                    )
                    confirm_password = st.text_input(
                        "Confirm New Password *",
                        type="password",
                        placeholder="Confirm your new password"
                    )
                
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    reset_button = st.form_submit_button("🔄 Reset Password", use_container_width=True)
                
                if reset_button:
                    # Validation
                    errors = []
                    
                    if not username or not email or not new_password or not confirm_password:
                        errors.append("Please fill in all required fields.")
                    
                    if new_password != confirm_password:
                        errors.append("New passwords do not match.")
                    
                    if len(new_password) < 6:
                        errors.append("Password must be at least 6 characters long.")
                    
                    if "@" not in email or "." not in email:
                        errors.append("Please enter a valid email address.")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                        return False
                    
                    try:
                        # Reset password
                        success = self.auth_service.reset_password(username, email, new_password)
                        
                        if success:
                            st.success("✅ Password reset successfully!")
                            st.info("🔐 You can now login with your new password.")
                            
                            # Auto-switch to login tab after short delay
                            st.balloons()
                            
                            # Clear form and switch to login
                            if st.button("🔐 Go to Login", use_container_width=True):
                                st.session_state.auth_tab = 0  # Switch to login tab
                                st.rerun()
                        
                    except AuthenticationError as e:
                        if "Invalid username or email" in str(e):
                            st.error("❌ Username and email combination not found. Please check your credentials.")
                        else:
                            st.error(f"❌ Password reset failed: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
            
            # Help section
            with st.expander("❓ Need Help?"):
                st.markdown("""
                **Password Reset Process:**
                1. Enter your exact username (case-sensitive)
                2. Enter the email address associated with your account
                3. Choose a new secure password
                4. Confirm your new password
                5. Click "Reset Password"
                
                **Troubleshooting:**
                - Make sure your username is spelled correctly
                - Use the exact email address from registration
                - Choose a password with at least 6 characters
                - Contact support if you still have issues
                
                **Security Note:**
                For security reasons, we verify both username and email before allowing password reset.
                """)
        
        return False
    
    def render_user_menu(self):
        """Render user menu in sidebar."""
        if not self.is_authenticated():
            return
        
        user = self.get_current_user()
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"### 👤 {t('user_account')}")
            st.markdown(f"**{user.full_name or user.username}**")
            
            # User stats
            try:
                stats = self.auth_service.get_user_stats(user.id)
                st.markdown(f"**{t('account_stats')}**")
                st.markdown(f"• {t('income_entries', stats['income_entries'])}")
                st.markdown(f"• {t('total_expenses', stats['total_expenses'])}")
                st.markdown(f"• {t('total_goals', stats['savings_goals'])}")
                st.markdown(f"• {t('member_since', stats['days_since_registration'])}")
            except Exception:
                pass
            
            if st.button(f"🚪 {t('logout')}", use_container_width=True):
                self.logout()
    
    def render_welcome_message(self):
        """Render welcome message for authenticated user."""
        if not self.is_authenticated():
            return
        
        user = self.get_current_user()
        # Language selector for authenticated users
        with st.sidebar:
            self.render_language_selector()
        
        st.markdown(f"# {t('welcome_message', user.full_name or user.username)}")


def check_authentication() -> Optional[UserProfile]:
    """
    Check if user is authenticated and return user profile.
    
    Returns:
        UserProfile if authenticated, None otherwise
    """
    auth_ui = AuthUI()
    if auth_ui.is_authenticated():
        return auth_ui.get_current_user()
    return None


def get_current_user_id() -> int:
    """
    Get current authenticated user ID.
    
    Returns:
        User ID
        
    Raises:
        ValueError: If no user is authenticated
    """
    auth_ui = AuthUI()
    user_id = auth_ui.get_current_user_id()
    if user_id is None:
        raise ValueError("No authenticated user")
    return user_id 