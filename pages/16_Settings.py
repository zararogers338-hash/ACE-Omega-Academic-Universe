"""ACE-Omega Page 16: Settings"""
import json, yaml
from pathlib import Path
import streamlit as st
from utils.theme import inject_theme
from utils.ace_model import check_all_backends, health_check, ollama_list_models, ollama_pull_model, load_gguf_from_upload
from utils.i18n import t

st.set_page_config(page_title="Settings | ACE-Omega", page_icon="⚙", layout="wide")
inject_theme()

st.markdown("# Settings")

st.markdown("### Backend Status")
mcfg = st.session_state.get("config",{}).get("model",{})
try:
    for name,s in check_all_backends(mcfg).items():
        ic = "🟢" if s.available else "🔴"
        st.markdown(f"""<div class="ace-card">
            <b>{ic} {name.upper()}</b>
            <span style="color:#8b8b94;margin-left:12px;">{s.info if s.available else s.error or 'Not configured'}</span>
            {'<br><span style="color:#55555e;font-size:11px;">Models: '+", ".join(s.models[:5])+'</span>' if s.models else ''}
        </div>""", unsafe_allow_html=True)
except Exception as e:
    st.error(str(e))

if st.button("Health Check", key="hc_settings"):
    with st.spinner("..."):
        r = health_check(mcfg)
        if r.error: st.error(f"{r.backend}: {r.error}")
        else: st.success(f"{r.backend} OK ({r.latency_ms:.0f}ms): {r.text[:100]}")

st.markdown("---")
st.markdown("### Ollama Model Manager")
oll_models, oll_err = ollama_list_models(mcfg)
if oll_err: st.caption(f"Ollama: {oll_err}")
else:
    if oll_models:
        for m in oll_models: st.markdown(f"  - `{m}`")
    pull_name = st.text_input("Pull model", placeholder="llama3, mistral...", key="set_pull_name")
    if pull_name and st.button("Pull", key="set_pull_btn"):
        prog = st.progress(0); status_t = st.empty()
        def upd(s, p): prog.progress(min(p,1.0)); status_t.caption(s)
        ok, err = ollama_pull_model(mcfg, pull_name, upd)
        if ok: st.success(f"Pulled {pull_name}")
        else: st.error(err)

st.markdown("---")
st.markdown("### GGUF Upload")
gf = st.file_uploader("Upload .gguf", type=["gguf"], key="set_gguf_up")
if gf and st.button("Load", key="set_gguf_load"):
    path = load_gguf_from_upload(gf.read(), gf.name)
    st.session_state.config.setdefault("model",{}).setdefault("gguf",{})["model_path"] = path
    st.success(f"Saved: {path}")

st.markdown("---")
st.markdown("### Formats")
st.markdown("CSV, JSON, XLSX, PDF, TXT, MD, DOCX, DOC, BibTeX")

st.markdown("---")
st.markdown("### Metaphor Legend")
for icon, concept, desc in [
    ("Celestial Body","Paper","Size = citations"),
    ("Satellite Ring","Follow-up cluster","Orbits core"),
    ("Asteroid Belt","Keyword fragments","Low-citation scattered"),
    ("Black Hole","Foundational paper","Citations > 50x mean"),
    ("Dyson Sphere","Paradigm capture","Top 1%"),
    ("Dyson Breach","Disruption","Anomalous impact"),
    ("Energy Leak","Open problem","Declining front"),
    ("Matrioshka Brain","Nested knowledge","Multi-generational"),
    ("Holographic","2D projection","Dimensionality reduction"),
    ("Observer Collapse","Interactive discovery","Quantum metaphor"),
]:
    st.markdown(f"**{icon}** = {concept} — {desc}")
