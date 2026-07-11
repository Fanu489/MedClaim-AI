import streamlit as st
import plotly.express as px

from database.db import run_query


def show_procedure_risk():

    st.title("🩺 Procedure Risk Analytics")

    procedures = run_query("""
        SELECT *
        FROM vw_procedure_risk
        ORDER BY procedure_denial_rate DESC
        LIMIT 20
    """)

    fig = px.bar(
        procedures,
        x="procedure_code",
        y="procedure_denial_rate",
        title="Highest Risk Procedures"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        procedures,
        use_container_width=True
    )