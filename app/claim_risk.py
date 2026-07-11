import streamlit as st
import pandas as pd
import joblib

# Load model once
@st.cache_resource
def load_model():
    return joblib.load("models/claim_denial_model.pkl")

model = load_model()

def show_claim_risk():

    st.title("🤖 Claim Risk Assessment")

    st.write(
        "Enter claim information to estimate denial risk."
    )

    # ==========================
    # INPUTS
    # ==========================

    billed_amount = st.number_input(
        "Billed Amount",
        min_value=0.0,
        value=5000.0
    )

    age = st.number_input(
        "Patient Age",
        min_value=0,
        max_value=120,
        value=40
    )

    length_of_stay = st.number_input(
        "Length of Stay",
        min_value=0,
        value=2
    )

    years_experience = st.number_input(
        "Provider Experience",
        min_value=0,
        value=10
    )

    procedure_cost = st.number_input(
        "Procedure Cost",
        min_value=0.0,
        value=1000.0
    )

    insurance_provider = st.selectbox(
        "Insurance Provider",
        [
            "Aetna",
            "BCBS",
            "Cigna",
            "Humana",
            "Medicaid",
            "Medicare",
            "UHC"
        ]
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "Insurance",
            "Cash",
            "Credit Card"
        ]
    )

    gender = st.selectbox(
        "Gender",
        [
            "Male",
            "Female"
        ]
    )

    insurance_type = st.selectbox(
        "Insurance Type",
        [
            "Private",
            "Government",
            "Employer"
        ]
    )

    visit_type = st.text_input(
        "Visit Type",
        "Outpatient"
    )

    department = st.text_input(
        "Department",
        "Cardiology"
    )

    admission_type = st.text_input(
        "Admission Type",
        "Emergency"
    )

    readmitted_flag = st.selectbox(
        "Readmitted",
        ["Yes", "No"]
    )

    diagnosis_code = st.text_input(
        "Diagnosis Code",
        "I10"
    )

    specialty = st.text_input(
        "Provider Specialty",
        "Cardiology"
    )

    procedure_code = st.text_input(
        "Procedure Code",
        "PROC001"
    )

    # ==========================
    # PREDICT
    # ==========================

    if st.button("Predict Claim Risk"):

        data = pd.DataFrame([{
            "billed_amount": billed_amount,
            "insurance_provider": insurance_provider,
            "payment_method": payment_method,
            "age": age,
            "gender": gender,
            "insurance_type": insurance_type,
            "visit_type": visit_type,
            "department": department,
            "admission_type": admission_type,
            "length_of_stay": length_of_stay,
            "readmitted_flag": readmitted_flag,
            "diagnosis_code": diagnosis_code,
            "specialty": specialty,
            "years_experience": years_experience,
            "procedure_code": procedure_code,
            "procedure_cost": procedure_cost
        }])

        prediction = model.predict(data)[0]

        probability = model.predict_proba(data)[0][1]

        risk_percent = round(probability * 100, 2)

        if risk_percent < 30:
            risk_level = "LOW"
        elif risk_percent < 70:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        st.success("Prediction Complete")

        col1, col2 = st.columns(2)

        col1.metric(
            "Risk Score",
            f"{risk_percent}%"
        )

        col2.metric(
            "Risk Level",
            risk_level
        )

        st.subheader("Recommendation")

        if risk_level == "HIGH":
            st.error(
                """
                Verify insurance eligibility.
                Validate diagnosis and procedure codes.
                Confirm prior authorization.
                Review documentation before submission.
                """
            )

        elif risk_level == "MEDIUM":
            st.warning(
                """
                Review claim carefully.
                Check coding accuracy.
                Confirm supporting documentation.
                """
            )

        else:
            st.success(
                """
                Low denial risk.
                Proceed with submission.
                """
            )