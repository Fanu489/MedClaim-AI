import streamlit as st
import plotly.express as px

from database.db import run_query


def show_provider_performance():

    st.title("👨‍⚕️ Provider Performance")

    providers = run_query("""
        SELECT *
        FROM vw_provider_risk
        ORDER BY provider_denial_rate DESC
        LIMIT 20
    """)

    fig = px.bar(
        providers,
        x="provider_id",
        y="provider_denial_rate",
        title="Provider Denial Rates"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        providers,
        use_container_width=True
    )