import pandas as pd
import joblib

from database.db import run_query
# =====================================
# LOAD TRAINED MODEL
# =====================================

model = joblib.load(
    "models/claim_denial_model.pkl"
)


# =====================================
# PREDICTION FUNCTION
# =====================================

def predict_claim_risk(
    billed_amount,
    insurance_provider,
    payment_method,
    age,
    gender,
    insurance_type,
    visit_type,
    department,
    admission_type,
    length_of_stay,
    readmitted_flag,
    diagnosis_code,
    specialty,
    years_experience,
    procedure_code,
    procedure_cost
):

    data = pd.DataFrame([
        {
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
        }
    ])

    probability = model.predict_proba(data)[0][1]

    if probability < 0.30:
        risk_level = "LOW"

    elif probability < 0.60:
        risk_level = "MEDIUM"

    else:
        risk_level = "HIGH"

    recommendations = []

    if risk_level == "HIGH":

        recommendations.append(
            "Review diagnosis and procedure coding."
        )

        recommendations.append(
            "Verify insurance eligibility."
        )

        recommendations.append(
            "Check prior authorization requirements."
        )

        recommendations.append(
            "Validate claim documentation."
        )

    elif risk_level == "MEDIUM":

        recommendations.append(
            "Perform claim quality review."
        )

        recommendations.append(
            "Verify patient coverage."
        )

    else:

        recommendations.append(
            "Claim appears low risk."
        )

    return {
        "risk_probability": round(probability * 100, 2),
        "risk_level": risk_level,
        "recommendations": recommendations
    }


# =====================================
# TEST
# =====================================

if __name__ == "__main__":

    result = predict_claim_risk(
        billed_amount=2500,
        insurance_provider="Medicaid",
        payment_method="Insurance",
        age=55,
        gender="Female",
        insurance_type="Government",
        visit_type="Outpatient",
        department="Oncology",
        admission_type="Emergency",
        length_of_stay=3,
        readmitted_flag=True,
        diagnosis_code="Z11.1",
        specialty="Oncology",
        years_experience=5,
        procedure_code="86580",
        procedure_cost=1500
    )

    print("\nPrediction Result")
    print(result)