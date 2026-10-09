
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="TellCo | Network Experience", layout="wide")
st.title("Network Experience")
st.caption("Customer-level network metrics and handset comparisons.")

data_path = Path(__file__).resolve().parents[1] / "customer_experience.csv"

if not data_path.exists():
    st.error("customer_experience.csv is missing from the dashboard folder.")
    st.stop()

df = pd.read_csv(data_path, dtype={"Customer_ID": "string"})
df["Customer_ID"] = df["Customer_ID"].str.replace(r"\.0$", "", regex=True)
df["Experience_cluster"] = df["Experience_cluster"].astype(str)
df["Handset Type"] = df["Handset Type"].fillna("Unknown")

metrics = {
    "Download throughput (kbps)": "Avg Bearer TP DL (kbps)",
    "Upload throughput (kbps)": "Avg Bearer TP UL (kbps)",
    "Download RTT (ms)": "Avg RTT DL (ms)",
    "Upload RTT (ms)": "Avg RTT UL (ms)",
    "Download TCP retransmissions (bytes)": "TCP DL Retrans. Vol (Bytes)",
    "Upload TCP retransmissions (bytes)": "TCP UL Retrans. Vol (Bytes)"
}

clusters = sorted(df["Experience_cluster"].unique())
selected = st.sidebar.multiselect(
    "Experience clusters", clusters, default=clusters
)
filtered = df[df["Experience_cluster"].isin(selected)].copy()

if filtered.empty:
    st.warning("Select at least one cluster.")
    st.stop()

st.info(
    "These customer averages use the missing-value and outlier treatment "
    "from the analysis. Replacement values can affect comparisons. "
    "Cluster numbers identify groups, not quality rankings."
)
st.caption(
    "DL means download; UL means upload. RTT measures network delay. "
    "All results below reflect the selected clusters."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(filtered):,}")
c2.metric(
    "Mean download speed (kbps)",
    f"{filtered['Avg Bearer TP DL (kbps)'].mean():,.2f}"
)
c3.metric(
    "Mean download RTT (ms)",
    f"{filtered['Avg RTT DL (ms)'].mean():.2f}"
)
c4.metric(
    "Mean DL retransmissions (bytes)",
    f"{filtered['TCP DL Retrans. Vol (Bytes)'].mean():,.2f}"
)

label = st.selectbox("Network metric to explore", list(metrics))
metric = metrics[label]

summary = filtered.groupby("Experience_cluster").agg(
    Customers=("Customer_ID", "size"),
    Mean_value=(metric, "mean"),
    Median_value=(metric, "median")
).reset_index()

left, right = st.columns(2)

with left:
    st.subheader("Customers by cluster")
    fig = px.bar(
        summary, x="Experience_cluster", y="Customers",
        color="Experience_cluster", text_auto=True,
        labels={"Experience_cluster": "Cluster"}
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Mean metric by cluster")
    fig = px.bar(
        summary, x="Experience_cluster", y="Mean_value",
        color="Experience_cluster", text_auto=".2f",
        labels={
            "Experience_cluster": "Cluster",
            "Mean_value": label
        }
    )
    st.plotly_chart(fig, width="stretch")

st.subheader("Cluster summary")
st.dataframe(
    summary.rename(columns={
        "Mean_value": f"Mean — {label}",
        "Median_value": f"Median — {label}"
    }).round(3),
    hide_index=True,
    width="stretch"
)

st.subheader("Compare the 10 most common handset types")
st.caption(
    "Handsets are selected by customer count within the chosen clusters. "
    "Each customer contributes their assigned handset and customer-level metric."
)

handsets = filtered.groupby("Handset Type").agg(
    Customers=("Customer_ID", "size"),
    Mean_value=(metric, "mean"),
    Median_value=(metric, "median")
).nlargest(10, "Customers").reset_index()

fig = px.bar(
    handsets.sort_values("Mean_value"),
    x="Mean_value",
    y="Handset Type",
    orientation="h",
    hover_data=["Customers", "Median_value"],
    labels={"Mean_value": label},
    height=500
)
st.plotly_chart(fig, width="stretch")
st.dataframe(handsets.round(3), hide_index=True, width="stretch")

st.subheader("Metric distribution by cluster")
fig = px.box(
    filtered,
    x="Experience_cluster",
    y=metric,
    color="Experience_cluster",
    points=False,
    labels={"Experience_cluster": "Cluster", metric: label}
)
st.plotly_chart(fig, width="stretch")
st.caption("Boxes summarize all selected customers; individual outlier points are hidden.")

st.download_button(
    "Download selected metric summary",
    data=summary.to_csv(index=False).encode("utf-8"),
    file_name="network_experience_summary.csv",
    mime="text/csv"
)
