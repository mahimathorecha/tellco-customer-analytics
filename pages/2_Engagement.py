
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="TellCo | Engagement", layout="wide")
st.title("Customer Engagement")
st.caption("Customer groups based on session frequency, duration, and traffic.")

data_path = Path(__file__).resolve().parents[1] / "engagement.csv"

if not data_path.exists():
    st.error("engagement.csv is missing from the dashboard folder.")
    st.stop()

df = pd.read_csv(data_path, dtype={"Customer_ID": "string"})
df["Customer_ID"] = df["Customer_ID"].str.replace(r"\.0$", "", regex=True)
df["Cluster"] = df["Cluster"].astype(str)

# Use explicit units for dashboard comparisons.
df["Duration_hours"] = df["Duration_seconds"] / 3600
df["Total_data_GB"] = df["Total Data (Bytes)"] / 1_000_000_000

clusters = sorted(df["Cluster"].unique())
selected = st.sidebar.multiselect(
    "Engagement clusters", clusters, default=clusters
)
filtered = df[df["Cluster"].isin(selected)].copy()

if filtered.empty:
    st.warning("Select at least one cluster.")
    st.stop()

st.info(
    "Clusters were formed using standardized engagement metrics. "
    "The figures below use original units. Cluster numbers are identifiers."
)
st.caption("All results reflect the selected engagement clusters.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(filtered):,}")
c2.metric("Mean sessions", f"{filtered['Session_count'].mean():.2f}")
c3.metric("Mean duration (hours)", f"{filtered['Duration_hours'].mean():.2f}")
c4.metric("Mean traffic (GB)", f"{filtered['Total_data_GB'].mean():.3f}")

summary = filtered.groupby("Cluster").agg(
    Customers=("Customer_ID", "size"),
    Mean_sessions=("Session_count", "mean"),
    Mean_duration_hours=("Duration_hours", "mean"),
    Mean_traffic_GB=("Total_data_GB", "mean")
).reset_index()

left, right = st.columns(2)

with left:
    st.subheader("Customers by cluster")
    fig = px.bar(
        summary, x="Cluster", y="Customers",
        color="Cluster", text_auto=True
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Compare cluster averages")
    comparisons = {
        "Mean sessions": "Mean_sessions",
        "Mean duration (hours)": "Mean_duration_hours",
        "Mean traffic (GB)": "Mean_traffic_GB"
    }
    label = st.selectbox("Comparison metric", list(comparisons))
    fig = px.bar(
        summary, x="Cluster", y=comparisons[label],
        color="Cluster", text_auto=".2f",
        labels={comparisons[label]: label}
    )
    st.plotly_chart(fig, width="stretch")

st.subheader("Cluster summary")
st.dataframe(summary.round(3), hide_index=True, width="stretch")

st.subheader("Detailed cluster statistics")
metrics = ["Session_count", "Duration_hours", "Total_data_GB"]
details = filtered.groupby("Cluster")[metrics].agg(
    ["min", "max", "mean", "sum"]
)
details.columns = [
    f"{metric} — {statistic}"
    for metric, statistic in details.columns
]
st.dataframe(details.round(3), width="stretch")

st.subheader("Top 10 customers")
ranking = {
    "Session count": "Session_count",
    "Duration (hours)": "Duration_hours",
    "Traffic (GB)": "Total_data_GB"
}
rank_label = st.selectbox("Rank by", list(ranking))
top10 = filtered.nlargest(10, ranking[rank_label])[
    ["Customer_ID", "Cluster", "Engagement_level"] + metrics
]
st.dataframe(top10.round(3), hide_index=True, width="stretch")

st.download_button(
    "Download engagement cluster summary",
    data=summary.to_csv(index=False).encode("utf-8"),
    file_name="engagement_cluster_summary.csv",
    mime="text/csv"
)
