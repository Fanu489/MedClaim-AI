import joblib

model = joblib.load("models/claim_denial_model.pkl")

classifier = model.named_steps["classifier"]

print(classifier.feature_importances_)