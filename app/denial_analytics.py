import streamlit as st
import plotly.express as px

from database.db import run_query


def show_denial_analytics():

    st.title("❌ Denial Analytics")

    reasons = run_query("""
        SELECT *
        FROM vw_top_denial_reasons
    """)

    fig = px.bar(
        reasons,
        x="total_denials",
        y="denial_reason",
        orientation="h",
        title="Top Denial Reasons"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        reasons,
        use_container_width=True
    )