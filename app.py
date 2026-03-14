import streamlit as st
import pandas as pd
from engine import load_data, recommend, recommend_researchers

st.set_page_config(page_title="Connect51 Partnership Opportunity Engine", layout="wide")

st.title("Connect51 Partnership Opportunity Engine")
st.write("Identify the institutions and researchers a university should collaborate with next.")

inst_df, res_df = load_data("institutions.csv","researchers.csv")

institution = st.sidebar.selectbox("Source institution", sorted(inst_df["institution_name"].unique()))
subject = st.sidebar.selectbox("Subject area", sorted(inst_df["subject_area"].unique()))

if st.sidebar.button("Generate Opportunities"):

    results = recommend(inst_df, institution, subject)
    researcher_results = recommend_researchers(res_df, results["institution_name"].tolist())

    col1,col2,col3 = st.columns(3)
    col1.metric("Top Match Score", int(results["match_score"].max()))
    col2.metric("Average Match Score", int(results["match_score"].mean()))
    col3.metric("Countries Represented", results["country"].nunique())

    st.subheader("Top Partner Institutions")
    st.dataframe(results[["institution_name","country","match_score","strategy_type"]], use_container_width=True)

    st.subheader("Partner Score Comparison")
    chart = results.set_index("institution_name")["match_score"]
    st.bar_chart(chart)

    st.subheader("Suggested Researchers")
    st.dataframe(researcher_results, use_container_width=True)

    if not results.empty:
        top_partner = results.iloc[0]["institution_name"]
        top_country = results.iloc[0]["country"]
        top_score = results.iloc[0]["match_score"]

        st.subheader("Strategy Insight")
        st.info(f"The strongest collaboration opportunity appears to be {top_partner} in {top_country} with a score of {top_score}.")

        st.subheader("Recommended Next Actions")
        st.success(f"1. Prioritise outreach to {top_partner}.")
        if not researcher_results.empty:
            st.success(f"2. Start with researcher introduction to {researcher_results.iloc[0]['researcher_name']}.")
        st.success("3. Focus collaboration around the highest‑scoring institutions.")