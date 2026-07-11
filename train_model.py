import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv("data/claim_training_dataset_final.csv")

print("\n" + "=" * 80)
print("MEDCLAIM AI - CLAIM DENIAL PREDICTION")
print("=" * 80)

print("\nDataset Shape:")
print(df.shape)

# =====================================================
# MISSING VALUES
# =====================================================

print("\nTop Missing Values:")
print(df.isnull().sum().sort_values(ascending=False).head(20))

# =====================================================
# REMOVE LEAKAGE COLUMNS
# =====================================================

drop_cols = [
    "record_id",
    "claim_id",

    # outcome leakage
    "paid_amount",
    "claim_status",
    "final_outcome",
    "denial_reason",
    "appeal_status",
    "appeal_filed",
    "appeal_resolution_date",
    "denial_reason_code",
    "denial_reason_description"
]

existing_drop_cols = [c for c in drop_cols if c in df.columns]

print("\nDropping Columns:")
print(existing_drop_cols)

df.drop(columns=existing_drop_cols, inplace=True)

# =====================================================
# TARGET
# =====================================================

y = df["target"]
X = df.drop(columns=["target"])

print("\nTarget Distribution:")
print(y.value_counts())

print("\nTarget Percentages:")
print((y.value_counts(normalize=True) * 100).round(2))

# =====================================================
# FEATURE TYPES
# =====================================================

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numerical_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()

print("\nCategorical Features:")
print(categorical_features)

print("\nNumerical Features:")
print(numerical_features)

# =====================================================
# PREPROCESSING
# =====================================================

numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]
)

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numerical_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

# =====================================================
# TRAIN TEST SPLIT
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

print("\nTraining Shape:", X_train.shape)
print("Testing Shape :", X_test.shape)

# =====================================================
# CLASS IMBALANCE
# =====================================================

negative = (y_train == 0).sum()
positive = (y_train == 1).sum()

scale_pos_weight = negative / positive

print("\nScale Pos Weight:", round(scale_pos_weight, 2))

# =====================================================
# MODELS
# =====================================================

models = {
    "Logistic Regression":
        LogisticRegression(
            max_iter=5000,
            class_weight="balanced",
            random_state=42
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=500,
            max_depth=12,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ),

    "XGBoost":
        XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            eval_metric="logloss"
        )
}

best_model = None
best_model_name = None
best_auc = 0

# =====================================================
# TRAINING LOOP
# =====================================================

for name, model in models.items():

    print("\n" + "=" * 80)
    print(f"TRAINING: {name}")
    print("=" * 80)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("smote", SMOTE(random_state=42)),
            ("classifier", model)
        ]
    )

    # Cross Validation

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    cv_scores = cross_val_score(
        pipeline,
        X_train,
        y_train,
        cv=cv,
        scoring="roc_auc",
        n_jobs=-1
    )

    print(
        f"\nCV ROC AUC: "
        f"{cv_scores.mean():.4f} "
        f"(+/- {cv_scores.std():.4f})"
    )

    # Train

    pipeline.fit(X_train, y_train)

    # Probabilities

    probabilities = pipeline.predict_proba(X_test)[:, 1]

    # Threshold Optimization

    best_threshold = 0.50
    best_threshold_f1 = 0

    for threshold in np.arange(0.10, 0.90, 0.01):

        preds = (probabilities >= threshold).astype(int)

        score = f1_score(
            y_test,
            preds,
            zero_division=0
        )

        if score > best_threshold_f1:
            best_threshold_f1 = score
            best_threshold = threshold

    predictions = (
        probabilities >= best_threshold
    ).astype(int)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    print(f"\nOptimal Threshold : {best_threshold:.2f}")
    print(f"Accuracy          : {accuracy:.4f}")
    print(f"Precision         : {precision:.4f}")
    print(f"Recall            : {recall:.4f}")
    print(f"F1 Score          : {f1:.4f}")
    print(f"ROC AUC           : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    if roc_auc > best_auc:
        best_auc = roc_auc
        best_model = pipeline
        best_model_name = name

# =====================================================
# SAVE MODEL
# =====================================================

joblib.dump(
    best_model,
    "models/claim_denial_model.pkl"
)

print("\n" + "=" * 80)
print("TRAINING COMPLETE")
print("=" * 80)

print(f"\nBest Model : {best_model_name}")
print(f"Best ROC AUC : {best_auc:.4f}")

print("\nModel Saved:")
print("models/claim_denial_model.pkl")