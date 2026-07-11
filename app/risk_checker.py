import streamlit as st
import pandas as pd
import joblib

from database.db import run_query

# ==================================================
# LOAD MODEL
# ==================================================

model = joblib.load("models/claim_denial_model.pkl")

# ==================================================
# PAGE
# ==================================================

def show_risk_checker():

    st.title("🤖 AI Claim Risk Checker")
    st.caption(
        "Predict denial risk before claim submission"
    )

    # ==================================================
    # DROPDOWNS
    # ==================================================

    insurance_df = run_query("""
        SELECT DISTINCT insurance_provider
        FROM claims_billing
        ORDER BY insurance_provider
    """)

    diagnosis_df = run_query("""
        SELECT DISTINCT diagnosis_code
        FROM diagnoses
        ORDER BY diagnosis_code
    """)

    procedure_df = run_query("""
        SELECT DISTINCT procedure_code
        FROM procedures
        ORDER BY procedure_code
    """)

    department_df = run_query("""
        SELECT DISTINCT department
        FROM encounters
        ORDER BY department
    """)

    specialty_df = run_query("""
        SELECT DISTINCT specialty
        FROM providers
        ORDER BY specialty
    """)

    # ==================================================
    # FORM
    # ==================================================

    with st.form("claim_form"):

        st.subheader("Claim Information")

        col1, col2 = st.columns(2)

        with col1:

            billed_amount = st.number_input(
                "Billed Amount",
                min_value=0.0,
                value=1000.0
            )

            age = st.number_input(
                "Patient Age",
                min_value=0,
                max_value=120,
                value=45
            )

            insurance_provider = st.selectbox(
                "Insurance Provider",
                insurance_df["insurance_provider"]
            )

            diagnosis_code = st.selectbox(
                "Diagnosis Code",
                diagnosis_df["diagnosis_code"]
            )

        with col2:

            procedure_code = st.selectbox(
                "Procedure Code",
                procedure_df["procedure_code"]
            )

            department = st.selectbox(
                "Department",
                department_df["department"]
            )

            specialty = st.selectbox(
                "Provider Specialty",
                specialty_df["specialty"]
            )

            gender = st.selectbox(
                "Gender",
                ["Male", "Female"]
            )

        submitted = st.form_submit_button(
            "🔍 Assess Claim Risk"
        )

    # ==================================================
    # PREDICTION
    # ==================================================

    if submitted:

        input_data = pd.DataFrame([{
            "billed_amount": billed_amount,
            "insurance_provider": insurance_provider,
            "payment_method": "Insurance",
            "age": age,
            "gender": gender,
            "insurance_type": "Commercial",
            "visit_type": "Outpatient",
            "department": department,
            "admission_type": "Elective",
            "length_of_stay": 1,
            "readmitted_flag": False,
            "diagnosis_code": diagnosis_code,
            "specialty": specialty,
            "years_experience": 10,
            "procedure_code": procedure_code,
            "procedure_cost": billed_amount * 0.40
        }])

        # ==========================================
        # ML PREDICTION
        # ==========================================

        probability = model.predict_proba(input_data)[0][1]

        ml_score = probability * 100

        # ==========================================
        # RISK FACTORS
        # ==========================================

        reasons = []

        diagnosis_risk = 0
        procedure_risk = 0
        provider_risk = 0

        # ------------------------------
        # Diagnosis Risk
        # ------------------------------

        diag = run_query(f"""
            SELECT diagnosis_denial_rate
            FROM vw_diagnosis_risk
            WHERE diagnosis_code = '{diagnosis_code}'
        """)

        if len(diag):

            diagnosis_risk = float(
                diag.iloc[0]["diagnosis_denial_rate"]
            )

            if diagnosis_risk > 10:
                reasons.append(
                    f"High-risk diagnosis ({diagnosis_risk:.1f}% denial rate)"
                )

        # ------------------------------
        # Procedure Risk
        # ------------------------------

        proc = run_query(f"""
            SELECT procedure_denial_rate
            FROM vw_procedure_risk
            WHERE procedure_code = '{procedure_code}'
        """)

        if len(proc):

            procedure_risk = float(
                proc.iloc[0]["procedure_denial_rate"]
            )

            if procedure_risk > 11:
                reasons.append(
                    f"Procedure has elevated denial history ({procedure_risk:.1f}%)"
                )

        # ==========================================
        # COMBINED SCORE
        # ==========================================

        risk_score = (
            ml_score * 0.7
            + diagnosis_risk * 0.15
            + procedure_risk * 0.15
        )

        risk_score = min(risk_score, 100)

        # ==========================================
        # LEVEL
        # ==========================================

        if risk_score >= 70:

            level = "🔴 HIGH RISK"

            color = "red"

        elif risk_score >= 40:

            level = "🟠 MEDIUM RISK"

            color = "orange"

        else:

            level = "🟢 LOW RISK"

            color = "green"

        # ==========================================
        # RESULTS
        # ==========================================

        st.divider()

        st.subheader("Assessment Result")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "AI Risk Score",
            f"{risk_score:.1f}%"
        )

        c2.metric(
            "Model Probability",
            f"{ml_score:.1f}%"
        )

        c3.metric(
            "Risk Level",
            level
        )

        st.divider()

        st.subheader("Risk Intelligence")

        r1, r2 = st.columns(2)

        r1.metric(
            "Diagnosis Risk",
            f"{diagnosis_risk:.2f}%"
        )

        r2.metric(
            "Procedure Risk",
            f"{procedure_risk:.2f}%"
        )

        st.divider()

        st.subheader("Detected Risk Factors")

        if reasons:

            for item in reasons:
                st.warning(item)

        else:

            st.success(
                "No major risk factors identified."
            )

        st.divider()

        st.subheader("Recommended Actions")

        st.write(
            "✅ Verify patient eligibility"
        )

        st.write(
            "✅ Confirm prior authorization requirements"
        )

        st.write(
            "✅ Review diagnosis and procedure coding"
        )

        st.write(
            "✅ Check payer-specific claim rules"
        )

        st.write(
            "✅ Validate claim before submission"
        )