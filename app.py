
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Connect51 Intelligence Platform", layout="wide")

st.markdown("""
<style>
header[data-testid="stHeader"] {display:none;}
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
.stApp {background: linear-gradient(180deg, rgb(10,40,60) 0%, rgb(6,24,36) 100%);}
.block-container {padding-top:2rem;}
.section-heading {color: rgb(236,92,60); font-size:28px; font-weight:700;}
.insight-box {
background: rgba(134,215,216,0.12);
border-left:6px solid rgb(134,215,216);
padding:16px;
border-radius:10px;
margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

def find_col(df, candidates):
    lower_map = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        key = cand.lower().strip()
        if key in lower_map:
            return lower_map[key]
    # partial contains match
    for c in df.columns:
        lc = c.lower().strip()
        for cand in candidates:
            if cand.lower().strip() in lc:
                return c
    return None

st.sidebar.title("Connect51 Intelligence Platform")
page = st.sidebar.radio("Platform Modules", ["Dashboard","Collaboration Network"])

collab = pd.read_csv("collaborators_clean.csv")
journals = pd.read_csv("journals_clean.csv")
sdg = pd.read_csv("sdg_collaborators_clean.csv")
geo = pd.read_csv("coauthor_countries_global_clean.csv")

# auto-detect columns
country_col = find_col(geo, ["country", "country_name", "co-author country", "coauthor_country", "country/region", "display_name"])
total_col = find_col(geo, ["work_count_total", "work_count", "count", "works_count", "total"])
lat_col = find_col(geo, ["latitude", "lat"])
lon_col = find_col(geo, ["longitude", "lon", "lng"])

# Fallback coordinates for common country names if missing
fallback_coords = {
    "United States": (39.8283, -98.5795),
    "USA": (39.8283, -98.5795),
    "China": (35.8617, 104.1954),
    "United Kingdom": (55.3781, -3.4360),
    "UK": (55.3781, -3.4360),
    "Australia": (-25.2744, 133.7751),
    "South Korea": (35.9078, 127.7669),
    "Japan": (36.2048, 138.2529),
    "Singapore": (1.3521, 103.8198),
    "Malaysia": (4.2105, 101.9758),
    "Germany": (51.1657, 10.4515),
    "Canada": (56.1304, -106.3468),
    "France": (46.2276, 2.2137),
    "India": (20.5937, 78.9629),
    "Taiwan": (23.6978, 120.9605),
}

def ensure_geo_columns(df):
    df = df.copy()
    if country_col is None:
        return df
    if lat_col is None or lon_col is None:
        df["latitude"] = df[country_col].map(lambda x: fallback_coords.get(str(x), (None, None))[0])
        df["longitude"] = df[country_col].map(lambda x: fallback_coords.get(str(x), (None, None))[1])
    else:
        df["latitude"] = pd.to_numeric(df[lat_col], errors="coerce")
        df["longitude"] = pd.to_numeric(df[lon_col], errors="coerce")
    return df

geo = ensure_geo_columns(geo)

if page=="Dashboard":
    st.title("Strategic Intelligence Scorecard")

    top_collab = collab.sort_values("mean_fwci", ascending=False).iloc[0]
    top_journal = journals.sort_values("mean_fwci", ascending=False).iloc[0]
    top_sdg = sdg.sort_values("mean_fwci", ascending=False).iloc[0]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Top Collaboration FWCI", round(float(top_collab["mean_fwci"]),2))
    c2.metric("Top Journal Impact", round(float(top_journal["mean_fwci"]),2))
    c3.metric("Top SDG Impact", round(float(top_sdg["mean_fwci"]),2))

    if country_col and total_col:
        top_country = geo.sort_values(total_col, ascending=False).iloc[0]
        c4.metric("Top Collaboration Country", str(top_country[country_col]))
        country_text = str(top_country[country_col])
    else:
        c4.metric("Top Collaboration Country", "Unavailable")
        country_text = "Unavailable"

    st.markdown(f"""
    <div class="insight-box">
    <b>AI Strategic Briefing</b><br><br>
    Strongest collaboration example: <b>{top_collab['institution_name']}</b> within <b>{top_collab['subject_name']}</b>.<br><br>
    Highest publishing impact journal: <b>{top_journal['journal_name']}</b>.<br><br>
    Strong SDG collaborator: <b>{top_sdg['institution_name']}</b>.<br><br>
    Dominant collaboration country: <b>{country_text}</b>.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Debug: detected geography columns"):
        st.write({
            "country_col": country_col,
            "total_col": total_col,
            "lat_col": lat_col,
            "lon_col": lon_col,
        })

if page=="Collaboration Network":
    st.title("Global Research Collaboration Network")

    if not country_col or not total_col:
        st.error("Could not detect the required country or total-count column in coauthor_countries_global_clean.csv.")
        st.dataframe(geo.head(20))
    else:
        network_df = geo.sort_values(total_col, ascending=False).head(8).copy()
        network_df = network_df.dropna(subset=["latitude", "longitude"])
        if network_df.empty:
            st.error("No usable latitude/longitude data found for the collaboration network.")
            st.dataframe(geo.head(20))
        else:
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

            arc = pdk.Layer(
                "ArcLayer",
                data=links_df,
                get_source_position='[source_lon,source_lat]',
                get_target_position='[target_lon,target_lat]',
                get_width="weight",
                get_source_color=[236,92,60],
                get_target_color=[134,215,216]
            )

            scatter = pdk.Layer(
                "ScatterplotLayer",
                data=nodes,
                get_position='[longitude,latitude]',
                get_radius="size",
                get_fill_color=[236,92,60],
                pickable=True
            )

            st.pydeck_chart(
                pdk.Deck(
                    layers=[arc,scatter],
                    initial_view_state=pdk.ViewState(latitude=20,longitude=10,zoom=1.2),
                    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
                    tooltip={"text": "{%s}" % country_col}
                )
            )

            st.markdown("""
            <div class="insight-box">
            <b>AI Network Insight</b><br><br>
            This network highlights the primary global research hubs and shows how knowledge flows
            across collaboration ecosystems. Connect51 can use this to identify strategic partnership pathways.
            </div>
            """, unsafe_allow_html=True)
