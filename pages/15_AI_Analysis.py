"""ACE-Omega Page 15: AI Analysis — scrollable output"""
import json, time
import streamlit as st
from utils.theme import inject_theme
from utils.i18n import t
from utils.ace_model import infer

st.set_page_config(page_title="AI Analysis | ACE-Omega", page_icon="🤖", layout="wide")
inject_theme()
L = lambda k: t(k, st.session_state.get("lang","en"))

st.markdown("# AI Analysis")
st.caption("Ask AI about patterns, paradigms, gaps, and insights.")

if not st.session_state.get("data_loaded"):
    st.warning("No data."); st.stop()

papers = st.session_state.papers
stats = st.session_state.stats

context = f"Dataset: {stats.get('total_papers',0)} papers, {stats.get('total_citations',0)} citations. "
context += f"Year range: {stats.get('year_min','?')}-{stats.get('year_max','?')}. "
context += f"Modules: {', '.join(f'{k}({v})' for k,v in stats.get('modules',{}).items())}. "
context += f"Black holes: {stats.get('blackholes',0)}, Dyson: {stats.get('dyson_spheres',0)}. "
context += f"Top: {'; '.join(f'{p.title[:40]}({p.cited_by_count})' for p in stats.get('top_5',[]))}."

st.markdown("### Quick Questions")
suggestions = [
    "What are the major paradigm shifts?",
    "Which papers are most foundational?",
    "What research gaps do you see?",
    "Summarize the field evolution.",
    "What emerging topics need attention?",
]
for sq in suggestions:
    if st.button(sq, key=f"sq_{hash(sq) % 100000}"):
        st.session_state._ai_query = sq

query = st.text_area("Or ask anything...", value=st.session_state.get("_ai_query",""), key="ai_q_main", height=80)

if st.button("Analyze", key="ai_btn_main", use_container_width=True):
    if not query: st.warning("Enter a question."); st.stop()
    with st.spinner("Analyzing..."):
        system = "You are ACE-Omega, an academic universe analysis AI. Analyze the dataset and answer. Be specific, cite paper titles. Respond in the user's language."
        full = f"Context:\n{context}\n\nQuestion: {query}"
        mcfg = st.session_state.config.get("model", {})
        r = infer(full, mcfg, system)

    if r.error:
        st.error(f"Error: {r.error}")
    else:
        # Scrollable container for AI output
        st.markdown(f"""<div style="max-height:400px;overflow-y:auto;background:#16161a;
            border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:16px;margin-top:8px;">
            <div style="margin-bottom:8px;">
                <span style="background:rgba(110,168,254,0.12);color:#6ea8fe;padding:2px 8px;border-radius:3px;font-size:10px;">{r.backend}</span>
                <span style="background:rgba(117,217,160,0.12);color:#75d9a0;padding:2px 8px;border-radius:3px;font-size:10px;margin-left:4px;">{r.latency_ms:.0f}ms</span>
            </div>
            <div style="color:#d4d4d8;font-size:14px;line-height:1.7;white-space:pre-wrap;">{r.text}</div>
        </div>""", unsafe_allow_html=True)
