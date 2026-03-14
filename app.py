
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Connect51 Intelligence Platform", layout="wide")

st.sidebar.title("Connect51 Intelligence Platform")
page = st.sidebar.radio("Platform Modules",["Dashboard","Collaboration Network"])

collab = pd.read_csv("collaborators_clean.csv")
journals = pd.read_csv("journals_clean.csv")
sdg = pd.read_csv("sdg_collaborators_clean.csv")
geo = pd.read_csv("coauthor_countries_global_clean.csv")

if page=="Dashboard":

    st.title("Strategic Intelligence Scorecard")

    top_collab = collab.sort_values("mean_fwci",ascending=False).iloc[0]
    top_journal = journals.sort_values("mean_fwci",ascending=False).iloc[0]
    top_sdg = sdg.sort_values("mean_fwci",ascending=False).iloc[0]
    top_country = geo.sort_values("work_count_total",ascending=False).iloc[0]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Top Collaboration FWCI",round(top_collab["mean_fwci"],2))
    c2.metric("Top Journal Impact",round(top_journal["mean_fwci"],2))
    c3.metric("Top SDG Impact",round(top_sdg["mean_fwci"],2))
    c4.metric("Top Collaboration Country",top_country["country"])

    st.markdown("### AI Strategic Briefing")
    st.write(
        f"Strongest collaboration: {top_collab['institution_name']} "
        f"in {top_collab['subject_name']}. "
        f"Top journal impact: {top_journal['journal_name']}. "
        f"Top SDG collaborator: {top_sdg['institution_name']}. "
        f"Dominant collaboration country: {top_country['country']}."
    )

if page=="Collaboration Network":

    st.title("Global Research Collaboration Network")

    network_df = geo.sort_values("work_count_total",ascending=False).head(8)

    nodes = network_df.copy()
    nodes["size"] = nodes["work_count_total"]*10

    links=[]
    rec=nodes.to_dict("records")
    for i in range(len(rec)):
        for j in range(i+1,len(rec)):
            links.append({
                "source_lat":rec[i]["latitude"],
                "source_lon":rec[i]["longitude"],
                "target_lat":rec[j]["latitude"],
                "target_lon":rec[j]["longitude"],
                "weight":1
            })

    links_df=pd.DataFrame(links)

    arc=pdk.Layer(
        "ArcLayer",
        data=links_df,
        get_source_position='[source_lon,source_lat]',
        get_target_position='[target_lon,target_lat]',
        get_width="weight",
        get_source_color=[236,92,60],
        get_target_color=[134,215,216]
    )

    scatter=pdk.Layer(
        "ScatterplotLayer",
        data=nodes,
        get_position='[longitude,latitude]',
        get_radius="size",
        get_fill_color=[236,92,60]
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[arc,scatter],
            initial_view_state=pdk.ViewState(latitude=20,longitude=10,zoom=1.2),
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        )
    )
