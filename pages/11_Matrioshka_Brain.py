"""ACE-Omega Page 11: Matrioshka Brain"""
import pandas as pd
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Matrioshka | ACE-Omega", page_icon="🔮", layout="wide")
inject_theme()
st.markdown("# Matrioshka Brain — Nested Knowledge")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
years = sorted(set(p.year for p in papers))
if len(years) < 4: st.info("Need 4+ years."); st.stop()

q1,q2,q3 = years[len(years)//4], years[len(years)//2], years[3*len(years)//4]
names = ["Core","Inner","Outer","Surface"]
ranges = [(min(years),q1),(q1+1,q2),(q2+1,q3),(q3+1,max(years))]
layers = {names[i]: [p for p in papers if lo<=p.year<=hi] for i,(lo,hi) in enumerate(ranges)}

cols = st.columns(4)
for i,(name,lp) in enumerate(layers.items()):
    with cols[i]: st.metric(name, len(lp)); st.caption(f"{sum(p.cited_by_count for p in lp):,} cites")

flow = pd.DataFrame([{"Layer":n,"Papers":len(lp),"Citations":sum(p.cited_by_count for p in lp)} for n,lp in layers.items()])
st.dataframe(flow, use_container_width=True, hide_index=True)
st.bar_chart(flow.set_index("Layer")["Papers"])
render_ai_analysis("Matrioshka Brain", f"4 knowledge layers, {len(papers)} papers.")
