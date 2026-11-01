import streamlit as st
import pandas as pd
import plotly.express as px
from engine import load_data, train_model, add_risk_scores, assign_action, load_rules, expected_rto_cost, prepaid_net_saving

st.set_page_config(page_title="COD Risk & RTO Control Tower", page_icon="📦", layout="wide")
st.title("COD Risk & RTO Control Tower")
st.caption("Pre-shipment decision support for a D2C Shopify brand")

@st.cache_data
def get_data():
    return load_data()

@st.cache_resource
def get_model(data_fingerprint):
    df = get_data()
    return train_model(df)

df = get_data()
rules = load_rules()
model, metrics = get_model(str(len(df)) + str(df["order_id"].nunique()))
scored = add_risk_scores(df, model)
scored["recommended_action"] = scored.apply(
    lambda r: assign_action(r, rules["risk_thresholds"]["low"], rules["risk_thresholds"]["high"]), axis=1
)

with st.sidebar:
    st.header("Business controls")
    low = st.slider("Medium-risk threshold", 0.05, 0.70, float(rules["risk_thresholds"]["low"]), 0.05)
    high = st.slider("High-risk threshold", 0.20, 0.95, float(rules["risk_thresholds"]["high"]), 0.05)
    discount = st.number_input("Prepaid discount (₹)", 0, 100, int(rules["prepaid"]["discount_rupees"]), 5)
    st.caption("Thresholds are editable for scenario testing. Persist changes in config/rules.yaml.")

scored["recommended_action"] = scored.apply(lambda r: assign_action(r, low, high), axis=1)
yesterday = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)
yday = scored[scored["order_datetime"].dt.date == yesterday.date()]
display_df = yday if len(yday) else scored.sort_values("order_datetime", ascending=False).head(100)

st.subheader("Yesterday's operational snapshot")
if len(yday) == 0:
    st.info("No records dated yesterday in this historical sample. Showing the latest 100 orders as a demo snapshot.")
counts = display_df["recommended_action"].value_counts()
c1,c2,c3,c4 = st.columns(4)
for col, label, key in [
    (c1,"Ship as-is","SHIP_AS_IS"),(c2,"WhatsApp confirmation","WHATSAPP_CONFIRM"),
    (c3,"Prepaid nudge","PREPAID_NUDGE"),(c4,"Hold / review","HOLD_REVIEW")]:
    col.metric(label, int(counts.get(key,0)))

st.divider()
st.subheader("Business impact estimates")
rto_cost = expected_rto_cost(rules)
net = (rules["prepaid"]["cod_rto_rate"] - rules["prepaid"]["prepaid_rto_rate"]) * rto_cost - discount
a,b,c = st.columns(3)
a.metric("Expected cost per RTO", f"₹{rto_cost:,.2f}")
b.metric("Net expected saving per prepaid conversion", f"₹{net:,.2f}")
c.metric("Model ROC-AUC", f"{metrics.get('roc_auc',0):.3f}" if "roc_auc" in metrics else "Unavailable")
st.caption("Impact is an assumption-based estimate, not realized savings. It excludes payment fees, discount uptake effects and genuine-order cancellations.")

left,right = st.columns(2)
with left:
    st.subheader("Historical delivery outcomes")
    outcomes = df["final_status"].value_counts().rename_axis("status").reset_index(name="orders")
    st.plotly_chart(px.pie(outcomes, names="status", values="orders", hole=0.45), use_container_width=True)
with right:
    st.subheader("Recommended action mix")
    action_counts = scored["recommended_action"].value_counts().rename_axis("action").reset_index(name="orders")
    st.plotly_chart(px.bar(action_counts, x="action", y="orders", color="action"), use_container_width=True)

st.subheader("Risk and decision explorer")
filters = st.multiselect("Filter action", sorted(scored["recommended_action"].unique()),
                         default=sorted(scored["recommended_action"].unique()))
view = scored[scored["recommended_action"].isin(filters)].copy()
view["ops_reason"] = view.apply(
    lambda r:
        "Hold for manual address/data review"
        if r["recommended_action"] == "HOLD_REVIEW"
        else "WhatsApp confirmation required"
        if r["recommended_action"] == "WHATSAPP_CONFIRM"
        else "Offer prepaid conversion discount"
        if r["recommended_action"] == "PREPAID_NUDGE"
        else "Low risk - proceed with dispatch",
    axis=1
)
cols = ["order_id","customer_name","city","order_value","customer_prior_orders","customer_prior_rto",
        "risk_score","recommended_action","ops_reason","final_status"]
st.dataframe(view[cols].sort_values("risk_score", ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download scored decision log", view[cols].to_csv(index=False).encode("utf-8"),
                   "decision_log.csv", "text/csv")

st.divider()
st.subheader("WhatsApp flow simulator")
order_ids = scored["order_id"].astype(str).tolist()
selected = st.selectbox("Select an order", order_ids)
order = scored[scored["order_id"].astype(str) == selected].iloc[0]
language = st.selectbox("Message language", ["English", "Hinglish"])
scenario = st.radio("Simulate customer response", ["YES", "NO", "No reply (24 hours)", "Random / unclear"], horizontal=True)
if language == "English":
    msg = f"Hi {order['customer_name']}, please confirm your COD order #{selected} worth ₹{order['order_value']}. Reply YES to confirm, NO to cancel, or choose prepaid and get ₹{discount} off."
else:
    msg = f"Hi {order['customer_name']}, your order #{selected} (₹{order['order_value']}) confirm karein. YES reply karein, NO se cancel karein, ya prepaid payment par ₹{discount} off paayein."
st.code(msg)
if st.button("Run simulation"):
    if scenario == "YES":
        st.success("Customer confirmed. Move order to dispatch queue.")
    elif scenario == "NO":
        st.warning("Customer declined. Cancel only after recording explicit confirmation.")
    elif scenario.startswith("No reply"):
        st.warning("No response after 24 hours. Keep on hold and send to manual review; do not silently cancel.")
    else:
        st.info("Unclear response. Route to human agent for clarification.")

st.subheader("Model evaluation")
st.write(metrics)
st.caption("Historical final_status is used as the label. Only delivered and RTO orders are labeled; in-transit orders are excluded. This is a baseline model, not a production guarantee.")
