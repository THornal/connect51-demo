import streamlit as st
import pandas as pd
from engine import load_data, recommend, recommend_researchers

st.title("Connect51 Partnership Opportunity Engine")

inst_df, res_df = load_data("institutions.csv","researchers.csv")

institution = st.selectbox("Select institution", inst_df["institution_name"].unique())
subject = st.selectbox("Subject area", inst_df["subject_area"].unique())

if st.button("Generate Opportunities"):
    results = recommend(inst_df, institution, subject)
    st.subheader("Recommended Partner Institutions")
    st.dataframe(results)

    rec_researchers = recommend_researchers(res_df, results["institution_name"].tolist())
    st.subheader("Suggested Researchers")
    st.dataframe(rec_researchers)