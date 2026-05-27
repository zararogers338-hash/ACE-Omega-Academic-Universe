"""ACE-Omega Page 07: Dyson Spheres"""
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Dyson Spheres | ACE-Omega", page_icon="⬡", layout="wide")
inject_theme()
st.markdown("# Dyson Spheres — Paradigm Capture")
st.caption("Papers capturing the majority of a domain's research energy.")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
dysons = sorted([p for p in papers if p.is_dyson], key=lambda x: -x.cited_by_count)
st.metric("Dyson Spheres", len(dysons))
if not dysons: st.info("None detected."); st.stop()

for dy in dysons:
    mp = [p for p in papers if p.module == dy.module]
    mt = sum(p.cited_by_count for p in mp)
    cap = dy.cited_by_count / max(mt, 1) * 100
    st.markdown(f"""<div class="ace-card">
        <b>{dy.title[:70]}</b><br>
        <span style="color:#8b8b94">{dy.authors[:40]} | {dy.year}</span><br>
        <span class="ace-badge b-blue">{dy.cited_by_count:,}</span>
        <span class="ace-badge b-green">Capture: {cap:.1f}%</span>
        <span class="ace-badge b-purple">{dy.module}</span>
    </div>""", unsafe_allow_html=True)

render_ai_analysis("Dyson Spheres", f"{len(dysons)} spheres.")
