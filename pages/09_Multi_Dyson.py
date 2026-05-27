"""ACE-Omega Page 09: Multi-Dyson Galaxy"""
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Multi-Dyson | ACE-Omega", page_icon="🌀", layout="wide")
inject_theme()
st.markdown("# Multi-Dyson Galaxy")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
mg = {}
for p in papers: mg.setdefault(p.module, []).append(p)
galaxies = {}
for mod, g in mg.items():
    if len(g) < 5: continue
    tops = sorted(g, key=lambda x: -x.cited_by_count)[:10]
    poles = []
    for tp in tops:
        if all(abs(tp.year - e.year) >= 3 for e in poles): poles.append(tp)
        if len(poles) >= 3: break
    if len(poles) >= 2: galaxies[mod] = poles

if not galaxies: st.info("No multi-paradigm modules."); st.stop()
st.metric("Multi-Paradigm Modules", len(galaxies))
for mod, poles in galaxies.items():
    st.markdown(f"### {mod}")
    cols = st.columns(len(poles))
    for i, pole in enumerate(poles):
        with cols[i]:
            st.markdown(f"""<div class="ace-card"><b>Pole {i+1}</b><br>{pole.title[:50]}<br>
                <span class="ace-badge b-blue">{pole.cited_by_count:,}</span>
                <span style="font-size:11px;color:#8b8b94">{pole.year}</span></div>""", unsafe_allow_html=True)
    st.markdown("---")
render_ai_analysis("Multi-Dyson", f"{len(galaxies)} multi-paradigm modules.")
