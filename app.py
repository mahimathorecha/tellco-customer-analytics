
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="TellCo Customer Analytics",
    page_icon="📊",
    layout="wide"
)

data_path = Path(__file__).parent / "customer_scores.csv"

if not data_path.exists():
    st.error("Place customer_scores.csv in the same folder as app.py.")
    st.stop()

df = pd.read_csv(data_path, dtype={"Customer_ID": "string"})
df["Customer_ID"] = df["Customer_ID"].str.replace(r"\.0$", "", regex=True)
df["Satisfaction_cluster"] = df["Satisfaction_cluster"].astype(str)

st.title("TellCo Customer Analytics")
st.caption("Project 5 | Customer satisfaction analysis")
st.info(
    "Satisfaction is a calculated proxy: the average of engagement "
    "and experience scores. It is not a customer survey rating. "
    "Cluster numbers identify groups; they are not rankings."
)

st.sidebar.header("Filters")
clusters = sorted(df["Satisfaction_cluster"].unique())
selected = st.sidebar.multiselect(
    "Satisfaction cluster", clusters, default=clusters
)

filtered = df[df["Satisfaction_cluster"].isin(selected)].copy()

if filtered.empty:
    st.warning("Select at least one cluster to display results.")
    st.stop()

st.caption("All figures below reflect the selected clusters.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(filtered):,}")
c2.metric("Mean engagement", f"{filtered['Engagement_score'].mean():.3f}")
c3.metric("Mean experience", f"{filtered['Experience_score'].mean():.3f}")
c4.metric("Mean satisfaction proxy", f"{filtered['Satisfaction_score'].mean():.3f}")

summary = filtered.groupby("Satisfaction_cluster").agg(
    Customers=("Satisfaction_score", "size"),
    Mean_engagement=("Engagement_score", "mean"),
    Mean_experience=("Experience_score", "mean"),
    Mean_satisfaction=("Satisfaction_score", "mean")
).reset_index()

left, right = st.columns(2)

with left:
    st.subheader("Customers by cluster")
    fig = px.bar(
        summary,
        x="Satisfaction_cluster",
        y="Customers",
        color="Satisfaction_cluster",
        text_auto=True,
        labels={"Satisfaction_cluster": "Cluster"}
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Mean satisfaction proxy by cluster")
    fig = px.bar(
        summary,
        x="Satisfaction_cluster",
        y="Mean_satisfaction",
        color="Satisfaction_cluster",
        text_auto=".3f",
        labels={
            "Satisfaction_cluster": "Cluster",
            "Mean_satisfaction": "Mean satisfaction proxy"
        }
    )
    st.plotly_chart(fig, width="stretch")

st.subheader("Cluster summary")
st.dataframe(summary.round(3), hide_index=True, width="stretch")

st.subheader("Engagement and experience")
sample = filtered.sample(n=min(5000, len(filtered)), random_state=42)
st.caption(f"Showing a reproducible sample of {len(sample):,} customers.")
fig = px.scatter(
    sample,
    x="Engagement_score",
    y="Experience_score",
    color="Satisfaction_cluster",
    opacity=0.5,
    labels={
        "Engagement_score": "Engagement score",
        "Experience_score": "Experience score",
        "Satisfaction_cluster": "Cluster"
    }
)
st.plotly_chart(fig, width="stretch")

st.subheader("Top 10 customers by satisfaction proxy")
top10 = filtered.sort_values("Satisfaction_score", ascending=False).head(10)
st.dataframe(top10.round(3), hide_index=True, width="stretch")

st.subheader("Find a customer")
st.caption("Customer IDs are replacement labels shared across the dashboard pages.")
customer_id = st.text_input("Enter the full Customer ID", placeholder="C000001")
if customer_id.strip():
    match = filtered[filtered["Customer_ID"] == customer_id.strip()]
    if match.empty:
        st.warning("No matching customer in the selected clusters.")
    else:
        st.dataframe(match, hide_index=True, width="stretch")

st.download_button(
    "Download filtered customer scores",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_customer_scores.csv",
    mime="text/csv"
)
