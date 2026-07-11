import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from database.db import run_query


def show_dashboard():

    st.title("🏥 MedClaim AI")
    st.subheader(
        "Intelligent Revenue Cycle & Claim Risk Management Platform"
    )

    # =====================================================
    # KPI SECTION
    # =====================================================

    claims = run_query("""
        SELECT *
        FROM vw_claims_summary
    """)

    revenue = run_query("""
        SELECT *
        FROM vw_revenue_summary
    """)

    total_claims = int(claims["total_claims"][0])
    denied_claims = int(claims["denied_claims"][0])
    denial_rate = float(claims["denial_rate"][0])
    revenue_lost = float(revenue["revenue_lost"][0])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Claims",
            f"{total_claims:,}"
        )

    with col2:
        st.metric(
            "Denied Claims",
            f"{denied_claims:,}"
        )

    with col3:
        st.metric(
            "Denial Rate",
            f"{denial_rate:.2f}%"
        )

    with col4:
        st.metric(
            "Revenue Lost",
            f"${revenue_lost:,.2f}"
        )

    st.divider()

    # =====================================================
    # DENIAL RATE GAUGE
    # =====================================================

    st.subheader("📊 Denial Rate Indicator")

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=denial_rate,
            number={"suffix": "%"},
            title={"text": "Current Denial Rate"},
            gauge={
                "axis": {"range": [0, 20]}
            }
        )
    )

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # INSURANCE PERFORMANCE
    # =====================================================

    insurance = run_query("""
        SELECT *
        FROM vw_insurance_performance
        ORDER BY denial_rate DESC
    """)

    reasons = run_query("""
        SELECT *
        FROM vw_top_denial_reasons
    """)

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🏢 Insurance Performance")

        fig1 = px.bar(
            insurance,
            x="insurance_provider",
            y="denial_rate",
            title="Denial Rate by Insurance Provider"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        st.download_button(
            "📥 Download Insurance Report",
            insurance.to_csv(index=False),
            file_name="insurance_performance.csv",
            mime="text/csv"
        )

    with col2:

        st.subheader("❌ Top Denial Reasons")

        fig2 = px.bar(
            reasons,
            x="total_denials",
            y="denial_reason",
            orientation="h",
            title="Most Common Denial Reasons"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # DEPARTMENT PERFORMANCE
    # =====================================================

    st.subheader("🏥 Department Performance")

    dept = run_query("""
        SELECT *
        FROM vw_department_performance
        ORDER BY denial_rate DESC
    """)

    fig3 = px.bar(
        dept,
        x="department",
        y="denial_rate",
        title="Department Denial Rate"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # HIGH RISK PROCEDURES
    # =====================================================

    procedures = run_query("""
        SELECT *
        FROM vw_procedure_risk
        ORDER BY procedure_denial_rate DESC
        LIMIT 10
    """)

    diagnosis = run_query("""
        SELECT *
        FROM vw_diagnosis_risk
        ORDER BY diagnosis_denial_rate DESC
        LIMIT 10
    """)

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("⚠️ High Risk Procedures")

        fig4 = px.bar(
            procedures,
            x="procedure_code",
            y="procedure_denial_rate",
            title="Highest Risk Procedure Codes"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    with col2:

        st.subheader("🩺 High Risk Diagnoses")

        fig5 = px.bar(
            diagnosis,
            x="diagnosis_code",
            y="diagnosis_denial_rate",
            title="Highest Risk Diagnosis Codes"
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

    st.divider()

    # =====================================================
    # HIGH RISK PROVIDERS
    # =====================================================

    st.subheader("👨‍⚕️ High Risk Providers")

    providers = run_query("""
        SELECT *
        FROM vw_provider_risk
        ORDER BY provider_denial_rate DESC
        LIMIT 10
    """)

    st.dataframe(
        providers,
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # REVENUE RECOVERY
    # =====================================================

    st.subheader("💰 Revenue Recovery Opportunity")

    st.success(
        f"""
        Current denied claims account for
        **${revenue_lost:,.2f}**
        in potentially recoverable revenue.

        By reducing denial rates through proactive
        claim risk management and denial prevention,
        healthcare organizations can significantly
        improve cash flow and financial performance.
        """
    )

    st.divider()

    # =====================================================
    # AI RECOMMENDATIONS
    # =====================================================

    st.subheader("🤖 AI Recommendations")

    st.info("""
### Recommended Actions

1. Review Oncology claims before submission.
2. Monitor Medicaid claims closely.
3. Validate diagnosis and procedure coding.
4. Focus on high-risk procedure codes.
5. Audit providers with elevated denial rates.
6. Address missing documentation before claim submission.
7. Prioritize prevention of duplicate claims.
8. Ensure prior authorizations are completed.
""")

    st.divider()

    st.caption(
        "MedClaim AI • Intelligent Revenue Cycle & Claim Risk Management Platform"
    )