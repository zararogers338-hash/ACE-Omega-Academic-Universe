"""ACE-Omega Page 13: Observer Collapse — FIXED duplicate key"""
import random
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Observer Collapse | ACE-Omega", page_icon="👁", layout="wide")
inject_theme()
st.markdown("# Observer Collapse")
st.caption("Papers exist in superposition until observed. Click to reveal.")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
if "observed" not in st.session_state:
    st.session_state.observed = set()

observed = st.session_state.observed
total = len(papers)
obs_count = sum(1 for p in papers if p.id in observed)

c1, c2, c3 = st.columns(3)
c1.metric("Observed", obs_count)
c2.metric("Superposed", total - obs_count)
c3.metric("Collapse %", f"{obs_count / max(total, 1) * 100:.1f}%")
st.progress(obs_count / max(total, 1))

if st.button("Observe Random", key="obs_rand_main"):
    unobs = [p for p in papers if p.id not in observed]
    if unobs:
        st.session_state.observed.add(random.choice(unobs).id)
        st.rerun()

cols_per_row = 4
for i in range(0, min(len(papers), 60), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= len(papers):
            break
        p = papers[idx]
        is_obs = p.id in observed
        with col:
            if is_obs:
                st.markdown(f"""<div class="ace-card" style="border-color:rgba(110,168,254,0.3);">
                    <b style="font-size:11px">{p.title[:35]}</b><br>
                    <span style="color:#8b8b94;font-size:10px">{p.year} | {p.cited_by_count}c</span>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button("???", key=f"obs_idx_{idx}", use_container_width=True):
                    st.session_state.observed.add(p.id)
                    st.rerun()

if st.button("Reset Observations", key="obs_reset_main"):
    st.session_state.observed = set()
    st.rerun()

render_ai_analysis("Observer Collapse", f"{obs_count}/{total} papers observed.")
