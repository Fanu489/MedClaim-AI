import streamlit as st

from app.dashboard import show_dashboard
from app.risk_checker import show_risk_checker
from app.revenue_analytics import show_revenue_analytics
from app.denial_analytics import show_denial_analytics
from app.provider_performance import show_provider_performance
from app.procedure_risk import show_procedure_risk
from app.system_info import show_system_info

st.set_page_config(
    page_title="MedClaim AI",
    page_icon="🏥",
    layout="wide"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Executive Dashboard",
        "🤖 AI Risk Checker",
        "💰 Revenue Analytics",
        "❌ Denial Analytics",
        "👨‍⚕️ Provider Performance",
        "🩺 Procedure Risk Analytics",
        "ℹ️ System Information"
    ]
)

if page == "🏠 Executive Dashboard":
    show_dashboard()

elif page == "🤖 AI Risk Checker":
    show_risk_checker()

elif page == "💰 Revenue Analytics":
    show_revenue_analytics()

elif page == "❌ Denial Analytics":
    show_denial_analytics()

elif page == "👨‍⚕️ Provider Performance":
    show_provider_performance()

elif page == "🩺 Procedure Risk Analytics":
    show_procedure_risk()

else:
    show_system_info()