import re
import yaml
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, recall_score
from sklearn.base import clone

DATA_PATH = "data/orders_sample.csv"

def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    df["final_status"] = df["final_status"].astype(str).str.strip().str.upper()
    df["payment_method"] = df["payment_method"].astype(str).str.strip().str.upper()
    df["order_datetime"] = pd.to_datetime(df["order_datetime"], errors="coerce")
    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    df["pincode"] = pd.to_numeric(df["pincode"], errors="coerce")
    for c in ["order_value", "num_items", "customer_prior_orders", "customer_prior_rto"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["address_length"] = df["address"].fillna("").astype(str).str.len()
    df["name_suspicious"] = df["customer_name"].fillna("").astype(str).str.lower().str.contains(
        r"test|asdf|qwerty|unknown|dummy|xxx|^[0-9]+$", regex=True
    ).astype(int)
    df["pincode_valid"] = df["pincode"].between(100000, 999999).astype(int)
    df["address_short"] = (df["address_length"] < 15).astype(int)
    df["prior_rto_rate"] = np.where(
        df["customer_prior_orders"].fillna(0) > 0,
        df["customer_prior_rto"].fillna(0) / df["customer_prior_orders"].replace(0, np.nan),
        0
    )
    df["target_rto"] = (df["final_status"] == "RTO").astype(int)
    return df

NUMERIC = ["order_value", "num_items", "customer_prior_orders", "customer_prior_rto",
           "address_length", "name_suspicious", "pincode_valid", "address_short", "prior_rto_rate"]
CATEGORICAL = ["city", "state", "utm_source", "courier", "payment_method"]

def train_model(df):
    train = df[df["final_status"].isin(["RTO", "DELIVERED"])].copy()
    X, y = train[NUMERIC + CATEGORICAL], train["target_rto"]
    if y.nunique() < 2 or len(train) < 30:
        return None, {"note": "Not enough labeled data to train a reliable model."}
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    pre = ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL)
    ])
    model = Pipeline([("prep", pre), ("rf", RandomForestClassifier(
        n_estimators=250, min_samples_leaf=4, class_weight="balanced", random_state=42
    ))])
    model.fit(X_train, y_train)
    p = model.predict_proba(X_test)[:, 1]
    pred = (p >= 0.5).astype(int)
    metrics = {
        "rows": int(len(train)),
        "test_rows": int(len(y_test)),
        "roc_auc": float(roc_auc_score(y_test, p)),
        "accuracy": float(accuracy_score(y_test, pred)),
        "rto_recall": float(recall_score(y_test, pred, zero_division=0))
    }
    return model, metrics

def add_risk_scores(df, model):
    out = df.copy()
    if model is None:
        # Conservative transparent fallback; not a trained prediction.
        score = (
            0.15 * (out["customer_prior_rto"].fillna(0) >= 1).astype(float) +
            0.25 * (out["prior_rto_rate"].fillna(0) >= 0.5).astype(float) +
            0.15 * out["address_short"] +
            0.10 * (1 - out["pincode_valid"]) +
            0.10 * out["name_suspicious"] +
            0.10 * (out["order_value"].fillna(0) >= out["order_value"].median()).astype(float)
        ).clip(0, 1)
        out["risk_score"] = score
    else:
        out["risk_score"] = model.predict_proba(out[NUMERIC + CATEGORICAL])[:, 1]
    return out

def assign_action(row, low=0.25, high=0.55):
    # Never auto-cancel based only on a model score.
    if row["risk_score"] >= high or row["address_short"] or not row["pincode_valid"] or row["name_suspicious"]:
        return "WHATSAPP_CONFIRM"
    if row["risk_score"] >= low:
        return "PREPAID_NUDGE"
    return "SHIP_AS_IS"

def expected_rto_cost(cfg):
    e = cfg["economics"]
    return e["forward_shipping"] + e["return_shipping"] + e["packaging_handling"] + e["damaged_rate"] * e["product_cost"]

def prepaid_net_saving(cfg):
    p = cfg["prepaid"]
    return (p["cod_rto_rate"] - p["prepaid_rto_rate"]) * expected_rto_cost(cfg) - p["discount_rupees"]

def load_rules():
    with open("config/rules.yaml", "r") as f:
        return yaml.safe_load(f)
