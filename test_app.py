import streamlit as st

st.title("🧪 Test App")
st.write("If you can see this, Streamlit is working!")

# Test basic functionality
st.sidebar.title("Sidebar Test")
st.sidebar.write("Sidebar content")

# Test form
with st.form("test_form"):
    name = st.text_input("Enter your name:")
    if st.form_submit_button("Submit"):
        st.success(f"Hello, {name}!")

# Test language imports
try:
    from budget_manager.utils.translations import t, Language, set_language
    st.success("✅ Translation imports working")
    
    set_language(Language.ENGLISH)
    st.write(f"Translation test: {t('app_title')}")
    
except Exception as e:
    st.error(f"❌ Translation error: {e}")

# Test auth imports
try:
    from auth_components import AuthUI
    st.success("✅ Auth imports working")
except Exception as e:
    st.error(f"❌ Auth error: {e}")

st.write("Test completed!") 