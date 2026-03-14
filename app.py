import streamlit as st
import pydeck as pdk
from engine import load_data, recommend, recommend_researchers

st.set_page_config(
    page_title="Connect51 Partnership Opportunity Engine",
    layout="wide"
)

st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Oswald:wght@700&display=swap");

html, body, [class*="css"] {
    font-family: "Montserrat", Arial, sans-serif;
    color: rgb(255, 255, 255);
}

.stApp {
    background: linear-gradient(180deg, rgb(10, 40, 60) 0%, rgb(6, 24, 36) 100%);
}

.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2rem;
}

.main-title {
    font-family: "Oswald", Arial, sans-serif;
    font-size: 2.9rem;
    font-weight: 700;
    color: rgb(236, 92, 60);
    text-transform: uppercase;
    line-height: 1.0;
    margin-bottom: 0.25rem;
    letter-spacing: 0.02em;
}

.brand-tagline {
    font-family: "Montserrat", Arial, sans-serif;
    color: rgb(255, 255, 255);
    font-size: 1.05rem;
    font-weight: 500;
    margin-bottom: 1.2rem;
}

.section-heading {
    font-family: "Oswald", Arial, sans-serif;
    color: rgb(236, 92, 60);
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.small-note, p, li, label, .stMarkdown, .stText {
    color: rgb(255, 255, 255) !important;
}

div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-left: 6px solid rgb(236, 92, 60);
    border-radius: 14px;
    padding: 0.3rem 0.6rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.18);
}

div[data-testid="stMetricLabel"] {
    color: rgb(255, 255, 255);
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: rgb(236, 92, 60);
    font-family: "Oswald", Arial, sans-serif;
}

.stButton > button {
    background-color: rgb(236, 92, 60);
    color: rgb(255, 255, 255);
    border: none;
    border-radius: 10px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: rgb(134, 215, 216);
    color: rgb(10, 40, 60);
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.04);
}

.insight-box {
    background: rgba(134, 215, 216, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-left: 6px solid rgb(134, 215, 216);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    color: rgb(255, 255, 255);
}

div[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
}

[data-testid="stInfo"], [data-testid="stSuccess"] {
    background: rgba(255, 255, 255, 0.06);
    color: rgb(255, 255, 255);
    border: 1px solid rgba(255, 255, 255, 0.10);
}
</style>
""", unsafe_allow_html=True)

inst_df, res_df = load_data("institutions.csv", "researchers.csv")

logo_col, title_col = st.columns([1.2, 4.8])
with logo_col:
    st.image("CONNECT51_WHITE.png", width=260)
with title_col:
    st.markdown('<div class="main-title">PARTNERSHIP OPPORTUNITY ENGINE</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tagline">Powering global connections in higher education</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="small-note">Identify the institutions and researchers a university should collaborate with next.</div>',
    unsafe_allow_html=True
)

st.sidebar.image("CONNECT51_WHITE.png", width=180)
st.sidebar.markdown("## Connect51 Controls")
institution = st.sidebar.selectbox("Source institution", sorted(inst_df["institution_name"].unique()))
subject = st.sidebar.selectbox("Subject area", sorted(inst_df["subject_area"].unique()))
show_density = st.sidebar.toggle("Show opportunity density layer", value=False)
show_country_summary = st.sidebar.toggle("Show country summary", value=True)
run = st.sidebar.button("Generate Opportunities", use_container_width=True)

if run:
    results = recommend(inst_df, institution, subject)
    researcher_results = recommend_researchers(res_df, results["institution_name"].tolist())

    top_score = int(results["match_score"].max()) if not results.empty else 0
    avg_score = int(results["match_score"].mean()) if not results.empty else 0
    countries = int(results["country"].nunique()) if not results.empty else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Top Match Score", top_score)
    c2.metric("Average Match Score", avg_score)
    c3.metric("Countries Represented", countries)

    st.markdown('<h3 class="section-heading">Top Partner Institutions</h3>', unsafe_allow_html=True)
    st.dataframe(
        results[["institution_name", "country", "match_score", "strategy_type"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown('<h3 class="section-heading">Global Opportunity Map</h3>', unsafe_allow_html=True)

    map_df = results.merge(
        inst_df[["institution_name", "country", "latitude", "longitude"]],
        on=["institution_name", "country"],
        how="left"
    ).dropna(subset=["latitude", "longitude"]).copy()

    if not map_df.empty:
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
                get_fill_color=[236, 92, 60, 220],
                get_line_color=[10, 40, 60, 255],
                line_width_min_pixels=2,
                stroked=True,
                pickable=True,
            )
        )

        if show_country_summary:
            country_summary = (
                map_df.groupby(["country", "latitude", "longitude"], as_index=False)
                .agg(opportunities=("institution_name", "count"),
                     average_match_score=("match_score", "mean"))
            )
            country_summary["label"] = country_summary.apply(
                lambda r: f"{r['country']}  {int(r['average_match_score'])}", axis=1
            )
            layers.append(
                pdk.Layer(
                    "TextLayer",
                    data=country_summary,
                    get_position="[longitude, latitude]",
                    get_text="label",
                    get_color=[10, 40, 60, 255],
                    get_size=14,
                    get_alignment_baseline="'top'",
                    get_pixel_offset=[0, 18],
                )
            )

        view_state = pdk.ViewState(latitude=18, longitude=10, zoom=0.9, pitch=0)

        tooltip = {
            "html": "<b>{institution_name}</b><br/>{country}<br/>Score: {match_score}<br/>{strategy_type}",
            "style": {"backgroundColor": "rgba(10, 40, 60, 0.95)", "color": "white"},
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip=tooltip,
                # CARTO map styles do not need a Mapbox token and render reliably on Streamlit Cloud
                map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            ),
            use_container_width=True,
        )

        if show_country_summary:
            st.markdown('<h3 class="section-heading">Country Opportunity Summary</h3>', unsafe_allow_html=True)
            country_table = (
                map_df.groupby("country", as_index=False)
                .agg(
                    opportunities=("institution_name", "count"),
                    average_match_score=("match_score", "mean")
                )
                .sort_values(["opportunities", "average_match_score"], ascending=False)
            )
            country_table["average_match_score"] = country_table["average_match_score"].round(1)
            st.dataframe(country_table, use_container_width=True, hide_index=True)

    st.markdown('<h3 class="section-heading">Partner Score Comparison</h3>', unsafe_allow_html=True)
    chart = results.set_index("institution_name")["match_score"]
    st.bar_chart(chart)

    st.markdown('<h3 class="section-heading">Suggested Researchers</h3>', unsafe_allow_html=True)
    st.dataframe(researcher_results, use_container_width=True, hide_index=True)

    if not results.empty:
        top_partner = results.iloc[0]["institution_name"]
        top_country = results.iloc[0]["country"]
        top_score = results.iloc[0]["match_score"]

        st.markdown('<h3 class="section-heading">Connect51 Strategy Insight</h3>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="insight-box">
            <b>AI Recommendation</b><br><br>
            The strongest immediate collaboration opportunity appears to be <b>{top_partner}</b> in <b>{top_country}</b>.<br><br>
            This institution leads the shortlist with a match score of <b>{top_score}</b>, indicating strong topic alignment,
            collaboration potential, and strategic relevance.<br><br>
            The map now uses a token-free light basemap so the geography renders clearly on Streamlit Cloud.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<h3 class="section-heading">Recommended Next Actions</h3>', unsafe_allow_html=True)
        st.success(f"1. Prioritise institutional outreach to {top_partner} in {top_country}.")
        if not researcher_results.empty:
            st.success(f"2. Begin with a researcher-level introduction to {researcher_results.iloc[0]['researcher_name']}.")
        st.success("3. Use the map, shortlist, and country summary together to shape a focused collaboration strategy.")
else:
    st.info("Use the controls on the left, then click 'Generate Opportunities'.")