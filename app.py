import streamlit as st
import pydeck as pdk
import pandas as pd
from engine import load_data, recommend, recommend_researchers

st.set_page_config(
    page_title="Connect51 Partnership Opportunity Engine",
    layout="wide"
)

st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Oswald:wght@700&display=swap");

header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

html, body, [class*="css"] {
    font-family: "Montserrat", Arial, sans-serif;
    color: rgb(255, 255, 255);
}

.stApp {
    background: linear-gradient(180deg, rgb(10,40,60) 0%, rgb(6,24,36) 100%);
}

.main-title {
    font-family: "Oswald", Arial, sans-serif;
    font-size: 3rem;
    color: rgb(236,92,60);
    text-transform: uppercase;
    line-height: 1.0;
    margin-bottom: 0.25rem;
}

.section-heading {
    font-family: "Oswald", Arial, sans-serif;
    color: rgb(236,92,60);
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.small-note, p, li, label, .stMarkdown, .stText {
    color: rgb(255, 255, 255) !important;
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-left: 6px solid rgb(236,92,60);
    border-radius: 14px;
    padding: 0.3rem 0.6rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18);
}

div[data-testid="stMetricLabel"] {
    color: rgb(255,255,255);
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: rgb(236,92,60);
    font-family: "Oswald", Arial, sans-serif;
}

.stButton > button {
    background-color: rgb(236,92,60);
    color: rgb(255,255,255);
    border: none;
    border-radius: 10px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: rgb(134,215,216);
    color: rgb(10,40,60);
}

[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
}

.insight-box {
    background: rgba(134,215,216,0.12);
    border: 1px solid rgba(255,255,255,0.10);
    border-left: 6px solid rgb(134,215,216);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    color: rgb(255,255,255);
}

div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
}

[data-testid="stInfo"], [data-testid="stSuccess"] {
    background: rgba(255,255,255,0.06);
    color: rgb(255,255,255);
    border: 1px solid rgba(255,255,255,0.10);
}
</style>
""", unsafe_allow_html=True)

inst_df, res_df = load_data("institutions.csv", "researchers.csv")

# Header
col1, col2 = st.columns([1,5])
with col1:
    st.image("CONNECT51_WHITE.png", width=220)
with col2:
    st.markdown('<div class="main-title">PARTNERSHIP OPPORTUNITY ENGINE</div>', unsafe_allow_html=True)
    st.write("Powering global connections in higher education")

st.write("Identify the institutions and researchers a university should collaborate with next.")

# Sidebar
st.sidebar.image("CONNECT51_WHITE.png", width=160)
st.sidebar.markdown("## Connect51 Controls")

institution = st.sidebar.selectbox(
    "Source institution",
    sorted(inst_df["institution_name"].unique())
)

subject = st.sidebar.selectbox(
    "Subject area",
    sorted(inst_df["subject_area"].unique())
)

show_density = st.sidebar.toggle("Show opportunity density layer", value=False)
show_country_summary = st.sidebar.toggle("Show country summary", value=True)
run = st.sidebar.button("Generate Opportunities", use_container_width=True)

def build_narrative(source_inst, results_df, researcher_df):
    top_partner = results_df.iloc[0]["institution_name"]
    top_country = results_df.iloc[0]["country"]
    top_score = int(results_df.iloc[0]["match_score"])
    country_counts = results_df["country"].value_counts()
    top_countries = ", ".join(country_counts.index.tolist()[:3])
    top_researcher = (
        researcher_df.iloc[0]["researcher_name"]
        if not researcher_df.empty else "a high-priority researcher contact"
    )
    return f"""
    Based on current research alignment, collaboration potential, and institutional strength,
    the most promising partnership opportunity for {source_inst} appears to be {top_partner} in {top_country}.

    The shortlist suggests the strongest opportunity clusters are concentrated in {top_countries}.
    This indicates Connect51 should prioritise outreach in these markets first, using the top-ranked
    institutions as anchor prospects for deeper partnership development.

    With a top match score of {top_score}, {top_partner} should be treated as the lead institutional target.
    The first practical next step is to begin with a researcher-level introduction, starting with {top_researcher},
    and build a targeted engagement plan around the top three institutions in the ranking.

    Overall, the current data indicates a focused, region-led partnership strategy is likely to generate the
    strongest results, especially where topic alignment and collaboration intensity are already high.
    """.strip()

if run:
    results = recommend(inst_df, institution, subject)
    researcher_results = recommend_researchers(res_df, results["institution_name"].tolist())

    top_score = int(results["match_score"].max())
    avg_score = int(results["match_score"].mean())
    countries = results["country"].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Top Match Score", top_score)
    c2.metric("Average Match Score", avg_score)
    c3.metric("Countries Represented", countries)

    st.markdown('<h3 class="section-heading">Top Partner Institutions</h3>', unsafe_allow_html=True)
    st.dataframe(
        results[["institution_name","country","match_score","strategy_type"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown('<h3 class="section-heading">Global Partnership Intelligence</h3>', unsafe_allow_html=True)
    top_partner = results.iloc[0]["institution_name"]
    top_country = results.iloc[0]["country"]
    country_counts = results["country"].value_counts().to_dict()
    strategy_text = f"""
    <div class="insight-box">
    <b>AI Strategic Insight</b><br><br>
    The strongest collaboration opportunity for <b>{institution}</b> appears to be
    <b>{top_partner}</b> located in <b>{top_country}</b>.<br><br>
    This partner ranks highest due to strong research alignment, collaboration potential,
    and institutional impact.<br><br>
    <b>Regional opportunity distribution:</b><br>
    {country_counts}<br><br>
    This suggests the most promising partnership clusters currently sit within these
    regions. A focused outreach strategy targeting the top-ranked institutions in
    these countries is likely to deliver the strongest collaboration outcomes.
    </div>
    """
    st.markdown(strategy_text, unsafe_allow_html=True)

    # Regional heat map summary panel
    st.markdown('<h3 class="section-heading">Opportunity Heat Map by Region</h3>', unsafe_allow_html=True)
    region_summary = (
        results.merge(inst_df[["institution_name", "region"]], on="institution_name", how="left")
        .groupby("region", as_index=False)
        .agg(opportunities=("institution_name", "count"),
             average_match_score=("match_score", "mean"))
        .sort_values(["opportunities", "average_match_score"], ascending=False)
    )
    region_summary["average_match_score"] = region_summary["average_match_score"].round(1)
    st.dataframe(region_summary, use_container_width=True, hide_index=True)
    region_chart = region_summary.set_index("region")["opportunities"]
    st.bar_chart(region_chart)

    st.markdown('<h3 class="section-heading">Global Opportunity Map</h3>', unsafe_allow_html=True)
    map_df = results.merge(
        inst_df[["institution_name","latitude","longitude","country"]],
        on=["institution_name","country"],
        how="left"
    ).dropna()

    map_df["size"] = map_df["match_score"] * 1800

    layers = []
    if show_density:
        layers.append(
            pdk.Layer(
                "HeatmapLayer",
                data=map_df,
                get_position="[longitude, latitude]",
                get_weight="match_score",
                radiusPixels=50,
                intensity=0.5,
                threshold=0.2,
            )
        )

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[longitude, latitude]",
            get_radius="size",
            get_fill_color=[236,92,60,220],
            get_line_color=[10,40,60,255],
            line_width_min_pixels=2,
            stroked=True,
            pickable=True
        )
    )

    view_state = pdk.ViewState(latitude=20, longitude=10, zoom=1.1)
    tooltip = {
        "html":"<b>{institution_name}</b><br/>{country}<br/>Score: {match_score}<br/>{strategy_type}",
        "style": {"backgroundColor":"rgba(10,40,60,0.95)", "color":"white"}
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        ),
        use_container_width=True
    )

    if show_country_summary:
        st.markdown('<h3 class="section-heading">Country Opportunity Summary</h3>', unsafe_allow_html=True)
        summary = (
            map_df.groupby("country")
            .agg(
                opportunities=("institution_name","count"),
                avg_score=("match_score","mean")
            )
            .reset_index()
        )
        summary["avg_score"] = summary["avg_score"].round(1)
        st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown('<h3 class="section-heading">Suggested Researchers</h3>', unsafe_allow_html=True)
    st.dataframe(researcher_results, use_container_width=True, hide_index=True)

    st.markdown('<h3 class="section-heading">AI Partnership Narrative</h3>', unsafe_allow_html=True)
    narrative = build_narrative(institution, results, researcher_results)
    st.markdown(f'<div class="insight-box">{narrative.replace(chr(10), "<br><br>")}</div>', unsafe_allow_html=True)

    st.download_button(
        "Download Strategy Briefing",
        data=narrative,
        file_name="connect51_strategy_briefing.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.markdown('<h3 class="section-heading">Recommended Next Actions</h3>', unsafe_allow_html=True)
    st.success(f"1. Prioritise institutional outreach to {top_partner} in {top_country}.")
    if not researcher_results.empty:
        st.success(f"2. Begin with a researcher-level introduction to {researcher_results.iloc[0]['researcher_name']}.")
    st.success("3. Use the map, regional heat map, and narrative briefing together to shape a focused collaboration strategy.")

else:
    st.info("Use the controls on the left and click 'Generate Opportunities'.")