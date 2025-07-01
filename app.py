"""
Smart Budget Manager - Web Interface
A beautiful and intuitive multi-user web application for managing your personal finances.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from decimal import Decimal
import calendar

# Configure page first with default title
st.set_page_config(
    page_title="Smart Budget Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our budget manager services
from budget_manager.services.budget_service import BudgetService
from budget_manager.services.expense_service import ExpenseService
from budget_manager.services.recommendation_service import RecommendationService
from budget_manager.core.models import ExpenseCategory
from budget_manager.utils.formatters import Formatters
from budget_manager.core.user_preferences import get_user_preferences, Currency
from budget_manager.utils.translations import t, Language, set_language, get_current_language, is_rtl
from auth_components import check_authentication, get_current_user_id, AuthUI

# Initialize language after imports
try:
    prefs = get_user_preferences()
    lang_code = prefs.get_language()
    language = Language(lang_code)
    set_language(language)
except:
    set_language(Language.ENGLISH)

# RTL CSS support for Arabic
if is_rtl():
    st.markdown("""
    <style>
    .main .block-container {
        direction: rtl;
        text-align: right;
    }
    .stSelectbox > label {
        direction: rtl;
    }
    .stMetric {
        direction: rtl;
    }
    .stHeader {
        direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication check - must be at the top
user = check_authentication()
if not user:
    # Show authentication form if user is not authenticated
    auth_ui = AuthUI()
    authenticated = auth_ui.render_auth_form()
    if not authenticated:
        st.stop()
    user = auth_ui.get_current_user()

user_id = get_current_user_id()

# Initialize services
@st.cache_resource
def get_services():
    return {
        'budget': BudgetService(),
        'expense': ExpenseService(),
        'recommendation': RecommendationService()
    }

services = get_services()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title(f"🏦 {t('navigation')}")

# Add user menu in sidebar
auth_ui = AuthUI()
auth_ui.render_user_menu()

page = st.sidebar.selectbox(
    t("choose_option"),
    [f"📊 {t('dashboard')}", f"💰 {t('income_goals')}", f"💸 {t('expenses')}", f"📈 {t('reports')}", f"⚙️ {t('settings')}"]
)

# Main title with user welcome
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f'<h1 class="main-header">💰 {t("welcome_message", user.full_name or user.username)}</h1>', unsafe_allow_html=True)
with col2:
    if st.button(f"🚪 {t('logout')}", key="main_logout"):
        auth_ui.logout()

def format_currency(amount):
    """Format currency with user preferences."""
    from decimal import Decimal
    return Formatters.format_currency(Decimal(str(amount)))

def create_progress_bar(current, target, label):
    """Create a custom progress bar."""
    if target > 0:
        progress = min(current / target, 1.0)
        percentage = (current / target) * 100
    else:
        progress = 0
        percentage = 0
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = percentage,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': label},
        delta = {'reference': 100},
        gauge = {
            'axis': {'range': [None, 150]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 100], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

# Dashboard Page
if page == f"📊 {t('dashboard')}":
    st.header(f"📊 {t('budget_dashboard')}")
    
    # Get current month data
    today = date.today()
    
    try:
        # Get recommendation and summary
        recommendation = services['recommendation'].get_daily_recommendation(user_id)
        summary = services['recommendation'].get_monthly_summary(user_id)
        alerts = services['recommendation'].get_smart_alerts(user_id)
        progress = services['recommendation'].get_savings_progress(user_id)
        
        if summary:
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label=f"💵 {t('monthly_income')}", 
                    value=format_currency(float(summary.total_income)),
                    delta=None
                )
            
            with col2:
                st.metric(
                    label=f"💸 {t('total_expenses')}", 
                    value=format_currency(float(summary.total_expenses)),
                    delta=f"-{format_currency(float(summary.total_expenses))}"
                )
            
            with col3:
                st.metric(
                    label=f"💰 {t('current_savings')}", 
                    value=format_currency(float(summary.actual_savings)),
                    delta=f"+{format_currency(float(summary.actual_savings))}"
                )
            
            with col4:
                st.metric(
                    label=f"🎯 {t('savings_target')}", 
                    value=format_currency(float(summary.savings_target)),
                    delta=None
                )
            
            # Daily recommendation section
            if recommendation:
                st.subheader(f"💡 {t('smart_recommendation')}")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.info(f"""
                    **Daily Spending Limit:** {format_currency(float(recommendation.recommended_daily_limit))}
                    
                    📅 **Days Remaining:** {recommendation.days_remaining}
                    
                    💸 **Spent This Month:** {format_currency(float(recommendation.current_month_spent))}
                    
                    📊 **Projected Savings:** {format_currency(float(recommendation.projected_savings))}
                    """)
                
                with col2:
                    # Progress gauge
                    if progress:
                        fig = create_progress_bar(
                            float(progress['current_savings']), 
                            float(progress['target_amount']), 
                            "Savings Progress"
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Alerts section
            if alerts:
                st.subheader("🔔 Smart Alerts")
                for alert in alerts:
                    severity = alert.get('severity', 'info')
                    message = alert.get('message', '')
                    
                    if severity == 'success':
                        st.success(f"✅ {message}")
                    elif severity == 'warning':
                        st.warning(f"⚠️ {message}")
                    elif severity == 'error':
                        st.error(f"❌ {message}")
                    else:
                        st.info(f"ℹ️ {message}")
            
            # Expense breakdown chart
            if summary.expense_by_category:
                st.subheader("📊 Expense Breakdown")
                
                # Prepare data for chart
                categories = list(summary.expense_by_category.keys())
                amounts = [float(amount) for amount in summary.expense_by_category.values()]
                
                # Create pie chart
                fig_pie = px.pie(
                    values=amounts, 
                    names=categories, 
                    title="Expenses by Category"
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                
                # Create bar chart
                prefs = get_user_preferences()
                currency_code = prefs.get_currency_code()
                chart_amount_label = f"Amount ({currency_code})"
                
                fig_bar = px.bar(
                    x=categories, 
                    y=amounts, 
                    title="Category Spending",
                    labels={'x': 'Category', 'y': chart_amount_label}
                )
                fig_bar.update_traces(marker_color='lightblue')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col2:
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            # Recent expenses
            recent_expenses = services['expense'].get_expenses(user_id, limit=5)
            if recent_expenses:
                st.subheader("💳 Recent Expenses")
                
                expense_data = []
                for expense in recent_expenses:
                    expense_data.append({
                        'Date': expense.expense_date.strftime('%Y-%m-%d'),
                        'Amount': float(expense.amount),
                        'Description': expense.description,
                        'Category': expense.category.value.title()
                    })
                
                df = pd.DataFrame(expense_data)
                st.dataframe(df, use_container_width=True)
        
        else:
            st.warning("⚠️ No budget data available. Please set up your income and savings goals first!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💰 Set Income", use_container_width=True):
                    st.switch_page("💰 Income & Goals")
            with col2:
                if st.button("💸 Add Expense", use_container_width=True):
                    st.switch_page("💸 Expenses")
    
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")

# Income & Goals Page
elif page == "💰 Income & Goals":
    st.header("💰 Income & Savings Goals")
    
    tab1, tab2 = st.tabs(["💵 Monthly Income", "🎯 Savings Goals"])
    
    with tab1:
        st.subheader("💵 Set Monthly Income")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Income form
            with st.form("income_form"):
                # Get user preferences for currency
                prefs = get_user_preferences()
                currency_label = Formatters.format_currency_input_label("Monthly Income")
                amount = st.number_input(currency_label, min_value=0.01, step=0.01, format="%.2f")
                description = st.text_input("Description (optional)", placeholder="e.g., Main salary")
                month_str = st.selectbox(
                    "Month", 
                    options=[f"{datetime.now().year}-{i:02d}" for i in range(1, 13)],
                    index=datetime.now().month - 1
                )
                
                if st.form_submit_button("💰 Set Income", use_container_width=True):
                    try:
                        month_date = datetime.strptime(month_str, "%Y-%m").date()
                        entry = services['budget'].add_income(
                            user_id=user_id,
                            amount=Decimal(str(amount)),
                            month=month_date,
                            description=description if description else None
                        )
                        st.success(f"✅ Income set: {format_currency(float(entry.amount))} for {month_date.strftime('%B %Y')}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error setting income: {str(e)}")
        
        with col2:
            # Current month income
            current_income = services['budget'].get_monthly_income(user_id, date.today())
            st.metric(
                "Current Month Income", 
                format_currency(float(current_income))
            )
            
            # Income history
            income_entries = services['budget'].get_income_entries(user_id)
            if income_entries:
                st.write("**Recent Entries:**")
                for entry in income_entries[-3:]:
                    st.write(f"• {format_currency(float(entry.amount))} - {entry.month.strftime('%b %Y')}")
    
    with tab2:
        st.subheader("🎯 Set Savings Goals")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Goals form
            with st.form("goal_form"):
                savings_label = Formatters.format_currency_input_label("Monthly Savings Target")
                target_amount = st.number_input(savings_label, min_value=0.01, step=0.01, format="%.2f")
                description = st.text_input("Goal Description (optional)", placeholder="e.g., Emergency fund")
                month_str = st.selectbox(
                    "Target Month", 
                    options=[f"{datetime.now().year}-{i:02d}" for i in range(1, 13)],
                    index=datetime.now().month - 1,
                    key="goal_month"
                )
                
                if st.form_submit_button("🎯 Set Goal", use_container_width=True):
                    try:
                        month_date = datetime.strptime(month_str, "%Y-%m").date()
                        goal = services['budget'].set_savings_goal(
                            user_id=user_id,
                            target_amount=Decimal(str(target_amount)),
                            month=month_date,
                            description=description if description else None
                        )
                        st.success(f"✅ Savings goal set: {format_currency(float(goal.target_amount))} for {month_date.strftime('%B %Y')}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error setting goal: {str(e)}")
        
        with col2:
            # Current goal
            current_goal = services['budget'].get_savings_goal(user_id, date.today())
            if current_goal:
                st.metric(
                    "Current Month Goal", 
                    format_currency(float(current_goal.target_amount))
                )
                if current_goal.description:
                    st.write(f"**Description:** {current_goal.description}")
            else:
                st.info("No savings goal set for current month")

# Expenses Page
elif page == "💸 Expenses":
    st.header("💸 Expense Management")
    
    tab1, tab2 = st.tabs(["➕ Add Expense", "📋 View Expenses"])
    
    with tab1:
        st.subheader("➕ Add New Expense")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Expense form
            with st.form("expense_form"):
                # Get user preferences for currency
                expense_label = Formatters.format_currency_input_label("Amount")
                amount = st.number_input(expense_label, min_value=0.01, step=0.01, format="%.2f")
                description = st.text_input("Description", placeholder="e.g., Lunch at restaurant")
                category = st.selectbox(
                    "Category", 
                    options=[cat.value for cat in ExpenseCategory],
                    format_func=lambda x: x.title()
                )
                expense_date = st.date_input("Date", value=date.today())
                
                if st.form_submit_button("💸 Add Expense", use_container_width=True):
                    try:
                        expense = services['expense'].add_expense(
                            user_id=user_id,
                            amount=Decimal(str(amount)),
                            description=description,
                            category=ExpenseCategory(category),
                            expense_date=expense_date
                        )
                        st.success(f"✅ Expense added: {format_currency(float(expense.amount))} - {expense.description}")
                        
                        # Show updated daily limit
                        recommendation = services['recommendation'].get_daily_recommendation(user_id)
                        if recommendation:
                            st.info(f"💡 Updated daily limit: {format_currency(float(recommendation.recommended_daily_limit))}")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding expense: {str(e)}")
        
        with col2:
            # Today's expenses
            today_expenses = services['expense'].get_today_expenses(user_id)
            today_total = sum(float(exp.amount) for exp in today_expenses)
            
            st.metric("Today's Spending", format_currency(today_total))
            
            if today_expenses:
                st.write("**Today's Expenses:**")
                for expense in today_expenses:
                    st.write(f"• {format_currency(float(expense.amount))} - {expense.description}")
    
    with tab2:
        st.subheader("📋 Expense History")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days_filter = st.selectbox("Time Period", [7, 30, 90, 365], index=1)
        
        with col2:
            category_filter = st.selectbox(
                "Category Filter", 
                ["All"] + [cat.value for cat in ExpenseCategory],
                format_func=lambda x: x.title() if x != "All" else x
            )
        
        with col3:
            limit = st.number_input("Number of Records", min_value=1, max_value=100, value=20)
        
        # Get filtered expenses
        start_date = date.today() - timedelta(days=days_filter)
        category_enum = ExpenseCategory(category_filter) if category_filter != "All" else None
        
        expenses = services['expense'].get_expenses(
            user_id=user_id,
            start_date=start_date,
            category=category_enum,
            limit=limit
        )
        
        if expenses:
            # Summary metrics
            total_amount = sum(float(exp.amount) for exp in expenses)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Amount", format_currency(total_amount))
            with col2:
                st.metric("Number of Expenses", len(expenses))
            with col3:
                avg_amount = total_amount / len(expenses) if expenses else 0
                st.metric("Average Amount", format_currency(avg_amount))
            
            # Expenses table
            expense_data = []
            for expense in expenses:
                expense_data.append({
                    'Date': expense.expense_date,
                    'Amount': float(expense.amount),
                    'Description': expense.description,
                    'Category': expense.category.value.title()
                })
            
            df = pd.DataFrame(expense_data)
            
            # Display as interactive table
            prefs = get_user_preferences()
            currency_code = prefs.get_currency_code()
            currency_format = f"{currency_code}%.2f"
            
            st.dataframe(
                df,
                use_container_width=True,
                column_config={
                    "Amount": st.column_config.NumberColumn(
                        "Amount",
                        format=currency_format
                    ),
                    "Date": st.column_config.DateColumn(
                        "Date",
                        format="YYYY-MM-DD"
                    )
                }
            )
            
            # Category breakdown for filtered data
            if len(expenses) > 1:
                category_totals = {}
                for expense in expenses:
                    cat = expense.category.value.title()
                    category_totals[cat] = category_totals.get(cat, 0) + float(expense.amount)
                
                # Update chart label with user's currency
                prefs = get_user_preferences()
                currency_code = prefs.get_currency_code()
                amount_label = f"Amount ({currency_code})"
                
                fig = px.bar(
                    x=list(category_totals.keys()),
                    y=list(category_totals.values()),
                    title=f"Spending by Category (Last {days_filter} days)",
                    labels={'x': 'Category', 'y': amount_label}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("No expenses found for the selected criteria.")

# Reports Page
elif page == "📈 Reports":
    st.header("📈 Reports & Analytics")
    
    tab1, tab2, tab3 = st.tabs(["📊 Monthly Report", "📈 Trends", "🎯 Goals Analysis"])
    
    with tab1:
        st.subheader("📊 Monthly Budget Report")
        
        # Month selector
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_month = st.selectbox(
                "Select Month",
                options=[f"{datetime.now().year}-{i:02d}" for i in range(1, 13)],
                index=datetime.now().month - 1
            )
        
        try:
            month_date = datetime.strptime(selected_month, "%Y-%m").date()
            summary = services['recommendation'].get_monthly_summary(user_id, month_date)
            
            if summary:
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💵 Income", format_currency(float(summary.total_income)))
                with col2:
                    st.metric("💸 Expenses", format_currency(float(summary.total_expenses)))
                with col3:
                    st.metric("💰 Savings", format_currency(float(summary.actual_savings)))
                with col4:
                    savings_rate = (float(summary.actual_savings) / float(summary.total_income) * 100) if summary.total_income > 0 else 0
                    st.metric("📊 Savings Rate", f"{savings_rate:.1f}%")
                
                # Visual breakdown
                col1, col2 = st.columns(2)
                
                with col1:
                    # Income vs Expenses vs Savings
                    fig = go.Figure(data=[
                        go.Bar(name='Income', x=['Financial Summary'], y=[float(summary.total_income)], marker_color='green'),
                        go.Bar(name='Expenses', x=['Financial Summary'], y=[float(summary.total_expenses)], marker_color='red'),
                        go.Bar(name='Savings', x=['Financial Summary'], y=[float(summary.actual_savings)], marker_color='blue')
                    ])
                    fig.update_layout(title="Income vs Expenses vs Savings", barmode='group')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Goal vs Actual
                    goal_vs_actual = go.Figure(go.Indicator(
                        mode = "number+gauge+delta",
                        value = float(summary.actual_savings),
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Savings Goal Achievement"},
                        delta = {'reference': float(summary.savings_target)},
                        gauge = {
                            'axis': {'range': [None, float(summary.savings_target) * 1.5]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, float(summary.savings_target)], 'color': "lightgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': float(summary.savings_target)
                            }
                        }
                    ))
                    goal_vs_actual.update_layout(height=400)
                    st.plotly_chart(goal_vs_actual, use_container_width=True)
                
                # Category breakdown
                if summary.expense_by_category:
                    st.subheader("💳 Expense Categories")
                    
                    categories = list(summary.expense_by_category.keys())
                    amounts = [float(amount) for amount in summary.expense_by_category.values()]
                    
                    # Create DataFrame for better display
                    category_df = pd.DataFrame({
                        'Category': [cat.title() for cat in categories],
                        'Amount': amounts,
                        'Percentage': [amount/sum(amounts)*100 for amount in amounts]
                    })
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.dataframe(
                            category_df,
                            column_config={
                                "Amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
                                "Percentage": st.column_config.NumberColumn("Percentage", format="%.1f%%")
                            },
                            use_container_width=True
                        )
                    
                    with col2:
                        fig_donut = px.pie(
                            values=amounts,
                            names=[cat.title() for cat in categories],
                            title="Category Distribution",
                            hole=0.4
                        )
                        st.plotly_chart(fig_donut, use_container_width=True)
            
            else:
                st.warning(f"No data available for {month_date.strftime('%B %Y')}")
                
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
    
    with tab2:
        st.subheader("📈 Spending Trends")
        
        # Get last 6 months of data
        months_data = []
        current_date = date.today().replace(day=1)
        
        for i in range(6):
            month_date = current_date - timedelta(days=32*i)
            month_date = month_date.replace(day=1)
            
            monthly_expenses = services['expense'].get_monthly_expenses(user_id, month_date)
            total_expenses = sum(float(exp.amount) for exp in monthly_expenses)
            
            months_data.append({
                'Month': month_date.strftime('%Y-%m'),
                'Total Expenses': total_expenses,
                'Number of Transactions': len(monthly_expenses)
            })
        
        months_data.reverse()  # Show chronologically
        
        if any(data['Total Expenses'] > 0 for data in months_data):
            df_trends = pd.DataFrame(months_data)
            
            # Spending trend chart
            fig_trend = px.line(
                df_trends, 
                x='Month', 
                y='Total Expenses',
                title='Monthly Spending Trend',
                markers=True
            )
            fig_trend.update_traces(line_color='blue', marker_size=8)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Transaction count trend
            fig_count = px.bar(
                df_trends, 
                x='Month', 
                y='Number of Transactions',
                title='Monthly Transaction Count',
                color='Number of Transactions'
            )
            st.plotly_chart(fig_count, use_container_width=True)
        
        else:
            st.info("Not enough data to show trends. Start adding expenses to see trends over time!")
    
    with tab3:
        st.subheader("🎯 Goals Analysis")
        
        # Savings progress
        progress = services['recommendation'].get_savings_progress(user_id)
        
        if progress:
            col1, col2 = st.columns(2)
            
            with col1:
                # Progress metrics
                st.metric("Target Amount", format_currency(progress['target_amount']))
                st.metric("Current Savings", format_currency(progress['current_savings']))
                st.metric("Progress", f"{progress['progress_percentage']:.1f}%")
                st.metric("Days Passed", f"{progress['days_passed']}/{progress['days_passed'] + progress['days_remaining']}")
            
            with col2:
                # Visual progress
                fig_progress = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = progress['progress_percentage'],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Goal Achievement"},
                    gauge = {
                        'axis': {'range': [None, 150]},
                        'bar': {'color': "darkgreen"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 100], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 100
                        }
                    }
                ))
                fig_progress.update_layout(height=400)
                st.plotly_chart(fig_progress, use_container_width=True)
            
            # Goal achievement prediction
            if progress['on_track']:
                st.success("✅ You're on track to meet your savings goal!")
            else:
                st.warning("⚠️ You may need to adjust your spending to meet your goal.")
                
                # Calculate required daily savings
                remaining_target = progress['target_amount'] - progress['current_savings']
                days_remaining = progress['days_remaining']
                
                if days_remaining > 0:
                    required_daily = remaining_target / days_remaining
                    st.info(f"💡 To reach your goal, you need to save {format_currency(required_daily)} per day for the remaining {days_remaining} days.")
        
        else:
            st.info("Set up your income and savings goals to see goal analysis.")

# Settings Page
elif page == "⚙️ Settings":
    st.header("⚙️ Application Settings")
    
    tab1, tab2 = st.tabs(["🗃️ Data Management", "📊 Preferences"])
    
    with tab1:
        st.subheader("🗃️ Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Export Data**")
            if st.button("📤 Export Expenses to CSV", use_container_width=True):
                try:
                    expenses = services['expense'].get_expenses(user_id, limit=1000)
                    if expenses:
                        expense_data = []
                        for expense in expenses:
                            expense_data.append({
                                'Date': expense.expense_date,
                                'Amount': float(expense.amount),
                                'Description': expense.description,
                                'Category': expense.category.value
                            })
                        
                        df = pd.DataFrame(expense_data)
                        csv = df.to_csv(index=False)
                        
                        st.download_button(
                            label="💾 Download CSV",
                            data=csv,
                            file_name=f"expenses_{date.today().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        st.warning("No expenses to export")
                except Exception as e:
                    st.error(f"Error exporting data: {str(e)}")
        
        with col2:
            st.write("**Database Info**")
            
            # Show database statistics
            try:
                total_expenses = len(services['expense'].get_expenses(user_id, limit=10000))
                total_income_entries = len(services['budget'].get_income_entries(user_id))
                total_goals = len(services['budget'].get_all_savings_goals(user_id))
                
                st.info(f"""
                📊 **Database Statistics:**
                - Total Expenses: {total_expenses}
                - Income Entries: {total_income_entries}
                - Savings Goals: {total_goals}
                """)
                
            except Exception as e:
                st.error(f"Error loading database info: {str(e)}")
        
        with col3:
            st.write("**Reset Database**")
            
            # Warning message
            st.warning("""
            ⚠️ **Danger Zone**
            
            This will permanently delete ALL your data:
            - Income entries
            - Expense records  
            - Savings goals
            - All historical data
            """)
            
            # Confirmation checkboxes
            confirm_reset = st.checkbox(
                "I understand this will delete all my data",
                key="confirm_reset_checkbox"
            )
            
            double_confirm = st.checkbox(
                "I am absolutely sure I want to proceed",
                key="double_confirm_checkbox",
                disabled=not confirm_reset
            )
            
            # Reset button (only enabled when both confirmations are checked)
            reset_enabled = confirm_reset and double_confirm
            
            if st.button(
                "🗑️ RESET DATABASE", 
                use_container_width=True,
                disabled=not reset_enabled,
                type="primary" if reset_enabled else "secondary",
                help="This action cannot be undone!"
            ):
                if reset_enabled:
                    try:
                        # Import the required functionality
                        from pathlib import Path
                        import os
                        from budget_manager.core.database import DatabaseManager
                        
                        # Get database path - try home directory first, fallback to current directory
                        try:
                            import os
                            if os.environ.get('STREAMLIT_CLOUD_DEPLOYMENT'):
                                data_dir = Path("./data")
                            else:
                                data_dir = Path.home() / ".budget_manager"
                            db_path = data_dir / "budget.db"
                        except (PermissionError, OSError):
                            data_dir = Path("./data")
                            db_path = data_dir / "budget.db"
                        
                        # Delete the database file
                        if db_path.exists():
                            os.remove(db_path)
                        
                        # Create fresh database with clean tables
                        DatabaseManager()
                        
                        # Clear the cached services to force recreation with new database
                        st.cache_resource.clear()
                        
                        # Show success message
                        st.success("✅ Database reset successfully! All data has been cleared.")
                        st.info("🔄 Refreshing page to show clean state...")
                        
                        # Auto-refresh the page after a short delay
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error resetting database: {str(e)}")
                        st.error("You can also reset manually by running: `python reset_database.py`")
                else:
                    st.error("⚠️ Please complete both confirmation steps before proceeding.")
            
            if not reset_enabled:
                if not confirm_reset:
                    st.caption("✓ Check both boxes above to enable the reset button")
                elif not double_confirm:
                    st.caption("✓ Please check the second confirmation box")
    
    with tab2:
        st.subheader("📊 Application Preferences")
        
        # Get current preferences
        prefs = get_user_preferences()
        
        # Currency selection
        st.write("**Currency Settings**")
        
        # Get currency choices and current selection
        currency_choices = [f"{curr.value['code']} ({curr.value['symbol']}) - {curr.value['name']}" for curr in Currency]
        current_currency = prefs.get_currency()
        current_choice = f"{current_currency.value['code']} ({current_currency.value['symbol']}) - {current_currency.value['name']}"
        
        # Find current index
        current_index = 0
        for i, choice in enumerate(currency_choices):
            if choice == current_choice:
                current_index = i
                break
        
        selected_currency = st.selectbox(
            "Currency Display",
            currency_choices,
            index=current_index,
            help="Select your preferred currency for display"
        )
        
        # Update currency if changed
        if selected_currency != current_choice:
            # Extract currency code from selection
            currency_code = selected_currency.split(' ')[0]
            try:
                new_currency = Currency[currency_code]
                prefs.set_currency(new_currency)
                st.success(f"✅ Currency updated to {new_currency.value['name']}")
                st.rerun()
            except KeyError:
                st.error("Invalid currency selection")
        
        # Display formatting options
        col1, col2 = st.columns(2)
        
        with col1:
            # Decimal places
            decimal_places = st.slider(
                "Decimal Places",
                min_value=0,
                max_value=4,
                value=prefs.get_decimal_places(),
                help="Number of decimal places to show in currency amounts"
            )
            
            if decimal_places != prefs.get_decimal_places():
                prefs.set_decimal_places(decimal_places)
                st.rerun()
        
        with col2:
            # Thousands separator
            group_thousands = st.checkbox(
                "Use Thousands Separator",
                value=prefs.get_group_thousands(),
                help="Show commas in large numbers (e.g., 1,000.00)"
            )
            
            if group_thousands != prefs.get_group_thousands():
                prefs.set_group_thousands(group_thousands)
                st.rerun()
        
        # Preview
        st.write("**Preview:**")
        sample_amount = Decimal("12345.67")
        formatted_preview = Formatters.format_currency(sample_amount)
        st.code(f"Sample amount: {formatted_preview}")
        
        st.divider()
        
        # Other preferences
        st.write("**Budget Settings**")
        
        # Target date preference
        target_day = st.slider(
            "Savings Target Day of Month", 
            min_value=1, 
            max_value=28, 
            value=prefs.get_savings_target_day(),
            help="Day of the month by which you want to achieve your savings goal"
        )
        
        if target_day != prefs.get_savings_target_day():
            prefs.set_savings_target_day(target_day)
            st.success(f"✅ Target day updated to {target_day}")
        
        st.divider()
        
        # Future features section
        st.write("**Coming Soon**")
        
        # Theme preference (placeholder for future feature)
        theme = st.selectbox(
            "Color Theme",
            ["Default", "Dark", "Light"],
            disabled=True,
            help="Theme selection (coming soon)"
        )
        
        # Reset preferences
        st.write("**Reset Preferences**")
        if st.button("🔄 Reset All Preferences to Defaults", use_container_width=True):
            prefs.reset_to_defaults()
            st.success("✅ All preferences reset to defaults")
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 1rem;'>
    💰 Smart Budget Manager | Built with ❤️ using Streamlit<br>
    Manage your finances intelligently and achieve your savings goals!
    </div>
    """, 
    unsafe_allow_html=True
) 