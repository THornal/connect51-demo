
import streamlit as st
import pandas as pd
from engine import load_data, recommend, recommend_researchers

st.set_page_config(
    page_title="Connect51 Partnership Opportunity Engine",
    layout="wide"
)

# ---------- Styling ----------
st.markdown("""
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtle {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1.2rem;
    }
    .insight-box {
        background-color: #f5f7fb;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e6eaf2;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Load data ----------
inst_df, res_df = load_data("institutions.csv", "researchers.csv")

# ---------- Header ----------
st.markdown('<div class="main-title">Connect51 Partnership Opportunity Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtle">Identify the institutions and researchers a university should collaborate with next.</div>',
    unsafe_allow_html=True
)

# ---------- Sidebar ----------
st.sidebar.header("Search Controls")

institution = st.sidebar.selectbox(
    "Source institution",
    sorted(inst_df["institution_name"].unique())
)

subject = st.sidebar.selectbox(
    "Subject area",
    sorted(inst_df["subject_area"].unique())
)

run = st.sidebar.button("Generate Opportunities")

# ---------- App body ----------
if run:
    results = recommend(inst_df, institution, subject)
    researcher_results = recommend_researchers(res_df, results["institution_name"].tolist())

    top_score = results["match_score"].max() if not results.empty else 0
    avg_score = round(results["match_score"].mean(), 1) if not results.empty else 0
    countries = results["country"].nunique() if not results.empty else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Top Match Score", f"{top_score}")
    c2.metric("Average Match Score", f"{avg_score}")
    c3.metric("Countries Represented", f"{countries}")

    st.markdown("### Top Partner Institutions")
    st.dataframe(results, use_container_width=True)

    if not results.empty:
        chart_df = results.set_index("institution_name")["match_score"]
        st.markdown("### Partner Score Comparison")
        st.bar_chart(chart_df)

    st.markdown("### Suggested Researchers")
    st.dataframe(researcher_results, use_container_width=True)

    if not results.empty:
        top_partner = results.iloc[0]["institution_name"]
        top_country = results.iloc[0]["country"]
        top_score = results.iloc[0]["match_score"]

        st.markdown("### Strategy Insight")
        st.markdown(
            f"""
            <div class="insight-box">
            <b>AI Summary:</b><br><br>
            Based on the selected institution and subject area, the strongest immediate partnership
            opportunity appears to be <b>{top_partner}</b> in <b>{top_country}</b>, with a match
            score of <b>{top_score}</b>.<br><br>
            This shortlist should be used as the starting point for targeted outreach, researcher-level
            introductions, and a more focused partnership development strategy.
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.info("Use the controls on the left, then click 'Generate Opportunities'.")
