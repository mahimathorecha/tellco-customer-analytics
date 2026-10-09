
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="TellCo | Usage", layout="wide")
st.title("Customer Usage")
st.caption("Session activity and application traffic across identified customers.")

data_path = Path(__file__).resolve().parents[1] / "customer_usage.csv"

if not data_path.exists():
    st.error("customer_usage.csv is missing from the dashboard folder.")
    st.stop()

df = pd.read_csv(data_path, dtype={"Customer_ID": "string"})
df["Customer_ID"] = df["Customer_ID"].str.replace(r"\.0$", "", regex=True)

df["Duration_hours"] = df["Duration_seconds"] / 3600
df["Total_data_GB"] = df["Total Data (Bytes)"] / 1_000_000_000

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(df):,}")
c2.metric("Total sessions", f"{df['Session_count'].sum():,.0f}")
c3.metric("Total traffic (GB)", f"{df['Total_data_GB'].sum():,.1f}")
c4.metric("Mean sessions per customer", f"{df['Session_count'].mean():.2f}")

st.caption("Traffic uses decimal units: 1 GB = 1,000,000,000 bytes.")

apps = [
    "Social Media", "Google", "Email",
    "Youtube", "Netflix", "Gaming", "Other"
]

traffic = pd.DataFrame({
    "Application": apps,
    "Traffic_GB": [
        df[f"{app} Total (Bytes)"].sum() / 1_000_000_000
        for app in apps
    ]
}).sort_values("Traffic_GB", ascending=False)

st.subheader("Traffic by application")
st.caption(
    "Application totals are shown separately from overall DL + UL traffic; "
    "they are not assumed to reconcile."
)
fig = px.bar(
    traffic,
    x="Application",
    y="Traffic_GB",
    text_auto=".1f",
    labels={"Traffic_GB": "Traffic (GB)"}
)
st.plotly_chart(fig, width="stretch")

st.subheader("Top 10 customers")
metrics = {
    "Session count": "Session_count",
    "Total duration (hours)": "Duration_hours",
    "Total traffic (GB)": "Total_data_GB",
}
for app in apps:
    metrics[f"{app} traffic (bytes)"] = f"{app} Total (Bytes)"

selection = st.selectbox("Rank customers by", list(metrics))
metric = metrics[selection]
top10 = df.nlargest(10, metric)[["Customer_ID", metric]]

fig = px.bar(
    top10,
    x="Customer_ID",
    y=metric,
    labels={metric: selection, "Customer_ID": "Customer ID"}
)
fig.update_xaxes(type="category")
st.plotly_chart(fig, width="stretch")
st.dataframe(top10, hide_index=True, width="stretch")

st.subheader("Session count distribution")
distribution = (
    df["Session_count"]
    .value_counts()
    .sort_index()
    .rename_axis("Sessions")
    .reset_index(name="Customers")
)
fig = px.bar(distribution, x="Sessions", y="Customers")
st.plotly_chart(fig, width="stretch")

st.download_button(
    "Download application traffic summary",
    data=traffic.to_csv(index=False).encode("utf-8"),
    file_name="application_traffic_summary.csv",
    mime="text/csv"
)
