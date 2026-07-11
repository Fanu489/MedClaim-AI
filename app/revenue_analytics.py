import streamlit as st
import plotly.express as px

from database.db import run_query


def show_revenue_analytics():

    st.title("💰 Revenue Analytics")

    revenue = run_query("""
        SELECT *
        FROM vw_revenue_summary
    """)

    st.metric(
        "Revenue Lost",
        f"${revenue['revenue_lost'][0]:,.2f}"
    )

    insurance = run_query("""
        SELECT
            insurance_provider,
            SUM(billed_amount) billed_amount,
            SUM(paid_amount) paid_amount
        FROM claims_billing
        GROUP BY insurance_provider
    """)

    fig = px.bar(
        insurance,
        x="insurance_provider",
        y=["billed_amount", "paid_amount"],
        barmode="group",
        title="Billed vs Paid Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )