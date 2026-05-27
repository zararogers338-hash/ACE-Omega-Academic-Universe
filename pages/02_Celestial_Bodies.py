"""
ACE-Omega Page 02: Celestial Bodies — Paper Explorer
"""
import math
import pandas as pd
import streamlit as st
from utils.theme import inject_theme
from utils.i18n import t
from utils.data_processor import MODULE_COLORS
from utils.components import render_ai_analysis

st.set_page_config(page_title="Celestial Bodies | ACE-Omega", page_icon="●", layout="wide")
inject_theme()
L = lambda k: t(k, st.session_state.get("lang","en"))

st.markdown("# Celestial Bodies")
st.caption("Every paper is a celestial body. Size proportional to citations + PageRank.")

if not st.session_state.get("data_loaded"):
    st.warning("No data. Go to **Home** to load."); st.stop()

papers = st.session_state.papers

fc1, fc2, fc3, fc4 = st.columns(4)
with fc1:
    modules = sorted(set(p.module for p in papers))
    sel_mod = st.multiselect("Module", modules, default=modules, key="cb_mod")
with fc2:
    min_cite = st.number_input("Min citations", 0, 100000, 0, key="cb_minc")
with fc3:
    years = sorted(set(p.year for p in papers))
    yr_range = st.select_slider("Year range", options=years, value=(min(years), max(years)), key="cb_yr") if len(years)>1 else (min(years), max(years))
with fc4:
    sort_by = st.selectbox("Sort", ["Citations desc", "Year desc", "Year asc", "Mass desc", "PageRank desc"], key="cb_sort")

timeline_year = st.session_state.get("timeline_year", 2026)
filtered = [p for p in papers if p.module in sel_mod and p.cited_by_count >= min_cite
    and yr_range[0] <= p.year <= yr_range[1] and p.year <= timeline_year]

search = st.session_state.get("global_search", "")
if search:
    sq = search.lower()
    filtered = [p for p in filtered if sq in p.title.lower() or sq in p.authors.lower() or sq in p.keywords.lower()]

if sort_by == "Citations desc": filtered.sort(key=lambda x: -x.cited_by_count)
elif sort_by == "Year desc": filtered.sort(key=lambda x: -x.year)
elif sort_by == "Year asc": filtered.sort(key=lambda x: x.year)
elif sort_by == "Mass desc": filtered.sort(key=lambda x: -x.mass)
elif sort_by == "PageRank desc": filtered.sort(key=lambda x: -x.pagerank)

st.markdown(f"**{len(filtered)}** papers shown")

df = pd.DataFrame([{
    "Type": ("BH" if p.is_blackhole else "DY" if p.is_dyson else "-"),
    "Title": p.title[:70], "Authors": p.authors[:40], "Year": p.year,
    "Citations": p.cited_by_count, "Mass": round(p.mass, 1),
    "Module": p.module, "Keywords": p.keywords[:50],
} for p in filtered])

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True, height=500)

st.markdown("---")
ec1, ec2 = st.columns(2)
with ec1:
    csv = df.to_csv(index=False).encode('utf-8') if not df.empty else b""
    st.download_button("Export CSV", csv, "celestial_bodies.csv", "text/csv", key="cb_csv")
with ec2:
    jdata = df.to_json(orient='records', force_ascii=False) if not df.empty else "[]"
    st.download_button("Export JSON", jdata, "celestial_bodies.json", "application/json", key="cb_json")

render_ai_analysis("Celestial Bodies", f"Showing {len(filtered)} papers. Sorted by {sort_by}.")
