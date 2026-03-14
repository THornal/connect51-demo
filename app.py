
import streamlit as st
import pandas as pd
import pydeck as pdk
from engine import load_data, recommend, recommend_researchers

st.set_page_config(page_title="Connect51 Intelligence Platform", layout="wide")

st.markdown("""
<style>
header[data-testid="stHeader"] {display:none;}
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
.stApp {background: linear-gradient(180deg, rgb(10,40,60) 0%, rgb(6,24,36) 100%);}
.block-container {padding-top:2rem; padding-bottom:2rem;}
html, body, [class*="css"] {color: white;}
.section-heading {color: rgb(236,92,60); font-size:28px; font-weight:700;}
.main-title {color: rgb(236,92,60); font-size: 3rem; font-weight: 800;}
.insight-box {background: rgba(134,215,216,0.12); border-left:6px solid rgb(134,215,216); padding:16px; border-radius:10px; margin-top:10px;}
.country-row { margin-bottom: 0.75rem; }
.country-label { display:flex; justify-content:space-between; font-weight:600; color:white; margin-bottom:0.2rem; }
.country-bar-bg { width:100%; background:rgba(255,255,255,0.08); border-radius:999px; height:14px; overflow:hidden; }
.country-bar-fill { height:14px; background:rgb(236,92,60); border-radius:999px; }
.country-subtext { font-size:0.9rem; color:rgba(255,255,255,0.85); margin-top:0.15rem; }
</style>
""", unsafe_allow_html=True)

def find_col(df, candidates):
    lower_map = {str(c).lower().strip(): c for c in df.columns}
    for cand in candidates:
        key = cand.lower().strip()
        if key in lower_map:
            return lower_map[key]
    for c in df.columns:
        lc = str(c).lower().strip()
        for cand in candidates:
            if cand.lower().strip() in lc:
                return c
    return None

def draw_country_bars(df, label_col, value_col, subtext_col=None):
    if df.empty:
        return
    max_val = df[value_col].max()
    for _, row in df.iterrows():
        width_pct = (row[value_col] / max_val) * 100 if max_val else 0
        subtext = f"Average match score: {row[subtext_col]}" if subtext_col else ""
        st.markdown(
            f"""
            <div class="country-row">
                <div class="country-label">
                    <span>{row[label_col]}</span>
                    <span>{int(row[value_col]) if float(row[value_col]).is_integer() else round(row[value_col],1)}</span>
                </div>
                <div class="country-bar-bg">
                    <div class="country-bar-fill" style="width: {width_pct}%;"></div>
                </div>
                {"<div class='country-subtext'>"+subtext+"</div>" if subtext else ""}
            </div>
            """,
            unsafe_allow_html=True
        )

@st.cache_data
def load_analysis_data():
    return {
        "collab": pd.read_csv("collaborators_clean.csv"),
        "journals": pd.read_csv("journals_clean.csv"),
        "sdg": pd.read_csv("sdg_collaborators_clean.csv"),
        "geo_global": pd.read_csv("coauthor_countries_global_clean.csv"),
        "geo_asia": pd.read_csv("coauthor_countries_asia_clean.csv"),
    }

def ensure_geo_columns(df):
    country_col = find_col(df, ["country","country_name","display_name"])
    lat_col = find_col(df, ["latitude","lat"])
    lon_col = find_col(df, ["longitude","lon","lng"])
    fallback_coords = {
        "United States": (39.8283, -98.5795), "USA": (39.8283, -98.5795),
        "China": (35.8617, 104.1954), "United Kingdom": (55.3781, -3.4360),
        "UK": (55.3781, -3.4360), "Australia": (-25.2744, 133.7751),
        "South Korea": (35.9078, 127.7669), "Japan": (36.2048, 138.2529),
        "Singapore": (1.3521, 103.8198), "Malaysia": (4.2105, 101.9758),
        "Germany": (51.1657, 10.4515), "Canada": (56.1304, -106.3468),
        "France": (46.2276, 2.2137), "India": (20.5937, 78.9629), "Taiwan": (23.6978, 120.9605)
    }
    out = df.copy()
    if country_col is None:
        return out
    if lat_col is None or lon_col is None:
        out["latitude"] = out[country_col].map(lambda x: fallback_coords.get(str(x), (None,None))[0])
        out["longitude"] = out[country_col].map(lambda x: fallback_coords.get(str(x), (None,None))[1])
    else:
        out["latitude"] = pd.to_numeric(out[lat_col], errors="coerce")
        out["longitude"] = pd.to_numeric(out[lon_col], errors="coerce")
    return out

# Load data
inst_df, res_df = load_data("institutions.csv","researchers.csv")
analysis = load_analysis_data()
collab = analysis["collab"]
journals = analysis["journals"]
sdg = analysis["sdg"]
geo_global = ensure_geo_columns(analysis["geo_global"])
geo_asia = ensure_geo_columns(analysis["geo_asia"])

# Detect cols
collab_inst_col = find_col(collab, ["institution_name","institution","display_name"])
collab_subject_col = find_col(collab, ["subject_name","subject"])
collab_fwci_col = find_col(collab, ["mean_fwci","fwci","avg_fwci"])

journal_name_col = find_col(journals, ["journal_name","display_name","journal","source_title","venue"])
journal_subject_col = find_col(journals, ["subject_name","subject"])
journal_fwci_col = find_col(journals, ["mean_fwci","fwci","avg_fwci"])

sdg_inst_col = find_col(sdg, ["institution_name","institution","display_name"])
sdg_fwci_col = find_col(sdg, ["mean_fwci","fwci","avg_fwci"])

country_col = find_col(geo_global, ["country","country_name","display_name"])
total_col = find_col(geo_global, ["work_count_total","work_count","count","works_count","total"])

# Header
col1, col2 = st.columns([1,5])
with col1:
    try:
        st.image("CONNECT51_WHITE.png", width=180)
    except Exception:
        pass
with col2:
    st.markdown('<div class="main-title">PARTNERSHIP OPPORTUNITY ENGINE</div>', unsafe_allow_html=True)
    st.write("Powering global connections in higher education")
st.write("This restored version includes both the original demo features and the analysis showcase.")

# Sidebar
st.sidebar.title("Connect51 Intelligence Platform")
module = st.sidebar.radio("Platform Modules", ["Dashboard", "Partnership Intelligence", "Analysis Showcase", "Collaboration Network"])

if module == "Dashboard":
    st.markdown('<div class="section-heading">Strategic Intelligence Scorecard</div>', unsafe_allow_html=True)
    top_collab = collab.sort_values(collab_fwci_col, ascending=False).iloc[0]
    top_journal = journals.sort_values(journal_fwci_col, ascending=False).iloc[0]
    top_sdg = sdg.sort_values(sdg_fwci_col, ascending=False).iloc[0]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Top Collaboration FWCI", round(float(top_collab[collab_fwci_col]),2))
    c2.metric("Top Journal Impact", round(float(top_journal[journal_fwci_col]),2))
    c3.metric("Top SDG Impact", round(float(top_sdg[sdg_fwci_col]),2))
    if country_col and total_col:
        top_country = geo_global.sort_values(total_col, ascending=False).iloc[0]
        c4.metric("Top Collaboration Country", str(top_country[country_col]))
        country_text = str(top_country[country_col])
    else:
        c4.metric("Top Collaboration Country", "Unavailable")
        country_text = "Unavailable"

    st.markdown(f"""
    <div class="insight-box">
    <b>AI Strategic Briefing</b><br><br>
    Strongest collaboration example: <b>{top_collab[collab_inst_col]}</b> within <b>{top_collab[collab_subject_col]}</b>.<br><br>
    Highest publishing impact journal: <b>{top_journal[journal_name_col]}</b>{f" in <b>{top_journal[journal_subject_col]}</b>" if journal_subject_col else ""}.<br><br>
    Strong SDG collaborator: <b>{top_sdg[sdg_inst_col]}</b>.<br><br>
    Dominant collaboration country: <b>{country_text}</b>.
    </div>
    """, unsafe_allow_html=True)

if module == "Partnership Intelligence":
    st.markdown('<div class="section-heading">Partnership Intelligence Demo</div>', unsafe_allow_html=True)
    institution = st.selectbox("Source institution", sorted(inst_df["institution_name"].unique()))
    subject = st.selectbox("Subject area", sorted(inst_df["subject_area"].unique()))
    results = recommend(inst_df, institution, subject)
    researcher_results = recommend_researchers(res_df, results["institution_name"].tolist())

    c1,c2,c3 = st.columns(3)
    c1.metric("Top Match Score", int(results["match_score"].max()))
    c2.metric("Average Match Score", int(results["match_score"].mean()))
    c3.metric("Countries Represented", int(results["country"].nunique()))

    st.markdown('<div class="section-heading">Top Partner Institutions</div>', unsafe_allow_html=True)
    st.dataframe(results[["institution_name","country","match_score","strategy_type"]], use_container_width=True, hide_index=True)

    st.markdown('<div class="section-heading">Opportunity Heat Map by Country</div>', unsafe_allow_html=True)
    country_summary = results.groupby("country", as_index=False).agg(opportunities=("institution_name","count"), average_match_score=("match_score","mean")).sort_values(["opportunities","average_match_score"], ascending=False)
    country_summary["average_match_score"] = country_summary["average_match_score"].round(1)
    st.dataframe(country_summary, use_container_width=True, hide_index=True)
    draw_country_bars(country_summary, "country", "opportunities", "average_match_score")

    st.markdown('<div class="section-heading">Suggested Researchers</div>', unsafe_allow_html=True)
    st.dataframe(researcher_results, use_container_width=True, hide_index=True)

if module == "Analysis Showcase":
    st.markdown('<div class="section-heading">Analysis Showcase</div>', unsafe_allow_html=True)
    subtab1, subtab2, subtab3, subtab4 = st.tabs(["Collaborators","Publishing","SDG","Geography"])

    with subtab1:
        subject_sel = st.selectbox("Select subject", sorted(collab[collab_subject_col].dropna().unique()), key="as1")
        subject_df = collab[collab[collab_subject_col] == subject_sel].sort_values(collab_fwci_col, ascending=False)
        st.dataframe(subject_df, use_container_width=True, hide_index=True)
        chart_df = collab.sort_values(collab_fwci_col, ascending=False).head(10)[[collab_inst_col, collab_fwci_col]].set_index(collab_inst_col)
        st.bar_chart(chart_df)

    with subtab2:
        subj_j = st.selectbox("Select subject", sorted(journals[journal_subject_col].dropna().unique()), key="as2")
        j_df = journals[journals[journal_subject_col] == subj_j].sort_values(journal_fwci_col, ascending=False)
        st.dataframe(j_df, use_container_width=True, hide_index=True)
        j_chart = journals.sort_values(journal_fwci_col, ascending=False).head(10)[[journal_name_col, journal_fwci_col]].set_index(journal_name_col)
        st.bar_chart(j_chart)

    with subtab3:
        st.dataframe(sdg, use_container_width=True, hide_index=True)
        sdg_chart = sdg.sort_values(sdg_fwci_col, ascending=False).head(10)[[sdg_inst_col, sdg_fwci_col]].set_index(sdg_inst_col)
        st.bar_chart(sdg_chart)

    with subtab4:
        left, right = st.columns(2)
        with left:
            st.markdown("**Global network**")
            gtop = geo_global.sort_values(total_col, ascending=False).head(10)[[country_col, total_col]]
            st.dataframe(gtop, use_container_width=True, hide_index=True)
            draw_country_bars(gtop, country_col, total_col)
        with right:
            country_col_asia = find_col(geo_asia, ["country","country_name","display_name"])
            total_col_asia = find_col(geo_asia, ["work_count_total","work_count","count","works_count","total"])
            atop = geo_asia.sort_values(total_col_asia, ascending=False).head(10)[[country_col_asia, total_col_asia]]
            st.markdown("**East & Southeast Asia network**")
            st.dataframe(atop, use_container_width=True, hide_index=True)
            draw_country_bars(atop, country_col_asia, total_col_asia)

if module == "Collaboration Network":
    st.markdown('<div class="section-heading">Global Research Collaboration Network</div>', unsafe_allow_html=True)
    if country_col and total_col:
        network_df = geo_global.sort_values(total_col, ascending=False).head(8).dropna(subset=["latitude","longitude"]).copy()
        nodes = network_df.copy()
        nodes["size"] = pd.to_numeric(nodes[total_col], errors="coerce").fillna(0) * 10
        links = []
        rec = nodes.to_dict("records")
        for i in range(len(rec)):
            for j in range(i+1, len(rec)):
                links.append({
                    "source_lat": rec[i]["latitude"],
                    "source_lon": rec[i]["longitude"],
                    "target_lat": rec[j]["latitude"],
                    "target_lon": rec[j]["longitude"],
                    "weight": 1
                })
        links_df = pd.DataFrame(links)
        arc = pdk.Layer("ArcLayer", data=links_df, get_source_position='[source_lon,source_lat]', get_target_position='[target_lon,target_lat]', get_width="weight", get_source_color=[236,92,60], get_target_color=[134,215,216])
        scatter = pdk.Layer("ScatterplotLayer", data=nodes, get_position='[longitude,latitude]', get_radius="size", get_fill_color=[236,92,60], pickable=True)
        st.pydeck_chart(pdk.Deck(layers=[arc,scatter], initial_view_state=pdk.ViewState(latitude=20,longitude=10,zoom=1.2), map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json", tooltip={"text": "{%s}" % country_col}))
        st.markdown("""
        <div class="insight-box">
        <b>AI Network Insight</b><br><br>
        This network highlights the primary global research hubs and shows how knowledge flows across collaboration ecosystems.
        </div>
        """, unsafe_allow_html=True)
