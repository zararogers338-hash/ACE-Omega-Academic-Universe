"""ACE-Omega Page 06: Black Holes"""
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Black Holes | ACE-Omega", page_icon="◉", layout="wide")
inject_theme()
st.markdown("# Black Holes — Foundational Papers")
st.caption("Papers with extreme influence.")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
blackholes = sorted([p for p in papers if p.is_blackhole], key=lambda x: -x.cited_by_count)
st.metric("Black Holes", len(blackholes))

if not blackholes:
    st.info("No black holes detected."); st.stop()

for bh in blackholes:
    trapped = len([p for p in papers if p.module == bh.module and p.year > bh.year and not p.is_blackhole])
    total_mod = max(1, len([p for p in papers if p.module == bh.module]))
    st.markdown(f"""<div class="ace-card">
        <b>{bh.title[:70]}</b><br>
        <span style="color:#8b8b94">{bh.authors[:40]} | {bh.year}</span><br>
        <span class="ace-badge b-red">{bh.cited_by_count:,} citations</span>
        <span class="ace-badge b-blue">{trapped} trapped ({trapped*100//total_mod}%)</span>
        <span class="ace-badge b-purple">Mass: {bh.mass:.1f}</span>
    </div>""", unsafe_allow_html=True)

render_ai_analysis("Black Holes", f"{len(blackholes)} black holes.")
