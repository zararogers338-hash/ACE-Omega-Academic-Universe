"""ACE-Omega Page 10: Energy Leak"""
import re
from collections import Counter
import pandas as pd
import streamlit as st
from utils.theme import inject_theme
from utils.components import render_ai_analysis

st.set_page_config(page_title="Energy Leak | ACE-Omega", page_icon="🔴", layout="wide")
inject_theme()
st.markdown("# Energy Leak — Open Problems")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
pk = ["open problem","future work","limitation","challenge","unsolved","gap","contradiction","debate","unresolved"]
lp, ls = [], Counter()
for p in papers:
    txt = (p.title+" "+p.abstract+" "+p.keywords).lower()
    sigs = [k for k in pk if k in txt]
    if sigs: lp.append({"p":p,"s":sigs}); [ls.update([s]) for s in sigs]

st.metric("Leak Papers", len(lp))
if ls:
    df = pd.DataFrame(ls.most_common(10), columns=["Signal","Count"])
    st.bar_chart(df.set_index("Signal")["Count"])
for item in sorted(lp, key=lambda x: -x["p"].cited_by_count)[:15]:
    p = item["p"]
    st.markdown(f'<div class="ace-card"><b>{p.title[:70]}</b><br><span style="color:#8b8b94">{p.year} | {p.cited_by_count}c</span> <span class="ace-badge b-red">{", ".join(item["s"])}</span></div>', unsafe_allow_html=True)
render_ai_analysis("Energy Leak", f"{len(lp)} leak papers.")
