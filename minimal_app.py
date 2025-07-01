"""
Minimal Budget Manager App - Authentication Only
"""

import streamlit as st

# Configure page
st.set_page_config(
    page_title="Budget Manager",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Minimal Budget Manager")
st.write("Testing basic functionality...")

# Test language system
try:
    from budget_manager.utils.translations import t, Language, set_language
    set_language(Language.ENGLISH)
    st.success(f"✅ Language: {t('app_title')}")
except Exception as e:
    st.error(f"❌ Language error: {e}")

# Test auth system
try:
    from auth_components import AuthUI
    st.success("✅ Auth system imported")
    
    auth_ui = AuthUI()
    st.success("✅ Auth UI created")
    
except Exception as e:
    st.error(f"❌ Auth error: {e}")

st.write("Minimal app test completed!")
