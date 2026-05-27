"""ACE-Omega Page 08: Dyson Breach"""
import numpy as np, pandas as pd
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Dyson Breach | ACE-Omega", page_icon="💥", layout="wide")
inject_theme()
st.markdown("# Dyson Breach — Disruptions")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
yg = {}
for p in papers: yg.setdefault(p.year, []).append(p)
breaches = []
for yr, g in sorted(yg.items()):
    if len(g) < 3: continue
    c = [p.cited_by_count for p in g]
    mu, sig = np.mean(c), max(np.std(c), 1)
    for p in g:
        z = (p.cited_by_count - mu) / sig
        if z > 2.0: breaches.append({"p": p, "z": z, "mu": mu})
breaches.sort(key=lambda x: -x["z"])
st.metric("Breaches", len(breaches))
if not breaches: st.info("None."); st.stop()
for b in breaches[:20]:
    p = b["p"]
    st.markdown(f"""<div class="ace-card"><b>{p.title[:70]}</b><br>
        <span style="color:#8b8b94">{p.authors[:40]} | {p.year}</span><br>
        <span class="ace-badge b-red">z={b['z']:.1f}</span>
        <span class="ace-badge b-blue">{p.cited_by_count:,}</span></div>""", unsafe_allow_html=True)
render_ai_analysis("Dyson Breach", f"{len(breaches)} breaches.")
