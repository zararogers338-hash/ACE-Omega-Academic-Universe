"""ACE-Omega Page 14: Timeline"""
import numpy as np, pandas as pd
import streamlit as st
from utils.theme import inject_theme
from utils.i18n import t
from utils.components import render_ai_analysis

st.set_page_config(page_title="Timeline | ACE-Omega", page_icon="⏳", layout="wide")
inject_theme()
L = lambda k: t(k, st.session_state.get("lang","en"))

st.markdown("# Timeline — Temporal Evolution")
st.caption("Publication trends, cumulative growth, paradigm shift detection, historical replay.")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
all_years = sorted(set(p.year for p in papers))

st.markdown("### Timeline Replay")
timeline_year = st.slider("Year cutoff", min(all_years), max(all_years), max(all_years), key="tl_year")
st.session_state.timeline_year = timeline_year

active = [p for p in papers if p.year <= timeline_year]
st.caption(f"{len(active)} papers up to {timeline_year}")

tl = pd.DataFrame([{"Year":p.year,"Citations":p.cited_by_count,"Module":p.module} for p in active])
if tl.empty: st.info("No papers."); st.stop()

yearly = tl.groupby("Year").agg(Papers=("Citations","count"),TotalCitations=("Citations","sum")).reset_index().sort_values("Year")

tab1,tab2,tab3 = st.tabs(["Publications","Cumulative","Module Growth"])
with tab1: st.line_chart(yearly.set_index("Year")["Papers"])
with tab2:
    yearly["Cumulative"] = yearly["TotalCitations"].cumsum()
    st.area_chart(yearly.set_index("Year")["Cumulative"])
with tab3:
    my = tl.groupby(["Year","Module"]).size().reset_index(name="Count")
    if not my.empty:
        pivot = my.pivot_table(index="Year",columns="Module",values="Count",fill_value=0)
        st.area_chart(pivot)

render_ai_analysis("Timeline", f"Timeline replay up to {timeline_year}. {len(active)} papers.")
