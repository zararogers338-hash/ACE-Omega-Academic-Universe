"""
ACE-Ω Academic Universe v3 — Main Entry (Home + Upload)
========================================================
Industrial minimal. Full sidebar with search, performance, model status.
"""

import json, time, logging, yaml
from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st

from utils.theme import inject_theme
from utils.i18n import t
from utils.file_parser import parse_file, normalize_dataframe, SUPPORTED_TYPES
from utils.data_processor import df_to_papers, compute_properties, generate_demo, compute_stats, papers_to_json
from utils.components import serialize_session, deserialize_session, L

# ─── Config ───
st.set_page_config(page_title="ACE-Ω Academic Universe", page_icon="🌌", layout="wide", initial_sidebar_state="expanded")
inject_theme()

CONFIG_PATH = Path("config.yaml")

def load_config():
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except: pass
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
    except: pass

# ─── Session State ───
defaults = {
    "lang": "en", "config": load_config(), "papers": [], "stats": {},
    "data_loaded": False, "degraded": False, "raw_df": None, "parse_log": [],
    "global_search": "", "timeline_year": 2026, "show_global_labels": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════
with st.sidebar:
    # Header row
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("#### 🌌 ACE-Ω")
    with c2:
        if st.button(L("lang_switch"), key="lang_sw"):
            st.session_state.lang = "zh" if st.session_state.lang == "en" else "en"
            st.rerun()

    # Global search
    search = st.text_input("🔍", placeholder=L("search_placeholder"), key="sidebar_search", label_visibility="collapsed")
    if search:
        st.session_state.global_search = search

    st.divider()

    # Backend selector
    st.markdown(f"**{L('backend_title')}**")
    mcfg = st.session_state.config.get("model", {})
    be = st.selectbox("Backend", ["openai", "ollama", "gguf", "fallback"],
        format_func=lambda x: {"openai": "OpenAI", "ollama": "Ollama", "gguf": "GGUF", "fallback": "Fallback"}.get(x, x),
        index=["openai","ollama","gguf","fallback"].index(mcfg.get("active_backend","openai"))
            if mcfg.get("active_backend","openai") in ["openai","ollama","gguf","fallback"] else 0,
        key="be_sel", label_visibility="collapsed")
    st.session_state.config.setdefault("model", {})["active_backend"] = be

    if be == "openai":
        with st.expander("API Config", expanded=False):
            ak = st.text_input("Key", value=mcfg.get("openai",{}).get("api_key",""), type="password", key="ak")
            bu = st.text_input("URL", value=mcfg.get("openai",{}).get("base_url","https://api.openai.com/v1"), key="bu")
            mn = st.text_input("Model", value=mcfg.get("openai",{}).get("model","gpt-4o-mini"), key="mn")
            if st.button("Save", key="sv_api"):
                st.session_state.config.setdefault("model",{}).setdefault("openai",{})
                st.session_state.config["model"]["openai"].update({"api_key":ak,"base_url":bu,"model":mn})
                save_config(st.session_state.config)
                st.success("✓")

    elif be == "ollama":
        with st.expander("Ollama Config", expanded=False):
            from utils.ace_model import ollama_list_models
            models_list, err = ollama_list_models(mcfg)
            if err:
                st.caption(f"⚠ {err}")
                model_name = st.text_input("Model name", value=mcfg.get("ollama",{}).get("model","llama3"), key="oll_mn")
            else:
                if models_list:
                    model_name = st.selectbox("Model", models_list,
                        index=models_list.index(mcfg.get("ollama",{}).get("model","llama3")) if mcfg.get("ollama",{}).get("model","llama3") in models_list else 0,
                        key="oll_sel")
                else:
                    model_name = st.text_input("Model name", value="llama3", key="oll_mn2")
            st.session_state.config.setdefault("model",{}).setdefault("ollama",{})["model"] = model_name

            pull_name = st.text_input("Pull new model", placeholder="e.g. llama3.2", key="oll_pull")
            if pull_name and st.button("Pull", key="oll_pull_btn"):
                with st.spinner(f"Pulling {pull_name}..."):
                    from utils.ace_model import ollama_pull_model
                    ok, perr = ollama_pull_model(mcfg, pull_name)
                    if ok: st.success(f"✓ {pull_name}")
                    else: st.error(perr)

    elif be == "gguf":
        with st.expander("GGUF Config", expanded=False):
            gguf_file = st.file_uploader("Upload .gguf", type=["gguf"], key="gguf_up")
            if gguf_file:
                from utils.ace_model import load_gguf_from_upload
                path = load_gguf_from_upload(gguf_file.read(), gguf_file.name)
                st.session_state.config.setdefault("model",{}).setdefault("gguf",{})["model_path"] = path
                save_config(st.session_state.config)
                st.success(f"✓ {gguf_file.name}")
            curr = mcfg.get("gguf",{}).get("model_path","")
            if curr and Path(curr).exists():
                st.caption(f"Current: {Path(curr).name}")

    st.divider()

    # Viz controls
    st.markdown(f"**{L('viz_controls')}**")
    vcfg = st.session_state.config.get("visualization", {})

    # ★ Global node label toggle
    show_labels = st.toggle(L("show_global_labels"), value=st.session_state.get("show_global_labels", False), key="gl_labels")
    st.session_state.show_global_labels = show_labels

    warp = st.slider(L("warp_strength"), 0.5, 5.0, float(vcfg.get("warp_strength", 2.0)), 0.1, key="warp")
    gd = st.slider(L("grid_density"), 50, 200, int(vcfg.get("gravity_grid_segments", 100)), 10, key="gd")
    pc = st.slider(L("particle_count"), 3000, 30000, int(vcfg.get("asteroid_particles", 12000)), 1000, key="pc")
    st.session_state.config.setdefault("visualization", {}).update(
        {"warp_strength": warp, "gravity_grid_segments": gd, "asteroid_particles": pc})

    st.divider()

    # Performance
    st.markdown(f"**{L('perf_title')}**")
    low_p = st.checkbox(L("low_particle"), value=vcfg.get("low_particle_mode", False), key="low_p")
    show_fps = st.checkbox(L("show_fps"), value=vcfg.get("fps_display", False), key="show_fps")
    st.session_state.config.setdefault("visualization", {}).update(
        {"low_particle_mode": low_p, "fps_display": show_fps})

    st.divider()

    # Data status
    if st.session_state.data_loaded:
        n = len(st.session_state.papers)
        st.markdown(f'<div class="info-bar">✅ {n} {L("paper_count")}</div>', unsafe_allow_html=True)

    # Model status
    st.markdown(f"**{L('model_status')}**")
    active_be = st.session_state.config.get("model",{}).get("active_backend","openai")
    st.caption(f"Backend: {active_be.upper()}")
    if st.button(L("health_check"), key="hc_btn"):
        with st.spinner("..."):
            from utils.ace_model import health_check
            r = health_check(st.session_state.config.get("model",{}))
            if r.error:
                st.error(f"✗ {r.error}")
            else:
                st.success(f"✓ {r.backend} · {r.latency_ms:.0f}ms")

    st.divider()

    # Session
    sc1, sc2 = st.columns(2)
    with sc1:
        if st.button(L("save_session"), key="save_sess"):
            data = serialize_session()
            st.download_button("⬇ Download", data, "ace_session.json", "application/json", key="dl_sess")
    with sc2:
        sess_file = st.file_uploader("Load", type=["json"], key="load_sess", label_visibility="collapsed")
        if sess_file:
            from utils.data_processor import Paper, compute_stats
            papers, meta = deserialize_session(sess_file.read().decode())
            st.session_state.papers = papers
            st.session_state.stats = compute_stats(papers)
            st.session_state.data_loaded = True
            st.session_state.lang = meta.get("lang", "en")
            st.rerun()


# ═══════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════
st.markdown(f"# 🌌 {L('app_title')}")
st.caption(L("app_subtitle"))

# Upload
st.markdown(f"### 📂 {L('upload_title')}")
st.caption(L("upload_desc"))
uploaded_files = st.file_uploader("Upload", type=SUPPORTED_TYPES, accept_multiple_files=True, key="uploader", label_visibility="collapsed")

col_demo, col_clear = st.columns([1, 1])
with col_demo:
    if st.button(f"🎲 {L('demo_button')}", key="demo", use_container_width=True):
        with st.spinner("Generating 120 papers..."):
            prog = st.progress(0)
            papers = generate_demo(120)
            prog.progress(80)
            st.session_state.papers = papers
            st.session_state.stats = compute_stats(papers)
            st.session_state.data_loaded = True
            st.session_state.parse_log = ["Demo: 120 papers generated."]
            prog.progress(100)
            time.sleep(0.3)
        st.rerun()
with col_clear:
    if st.button("🗑 Clear", key="clear", use_container_width=True):
        for k in ["papers","stats","data_loaded","raw_df","parse_log"]:
            st.session_state[k] = [] if k in ["papers","parse_log"] else ({} if k == "stats" else (False if k == "data_loaded" else None))
        st.rerun()

# Process uploads
if uploaded_files:
    all_dfs, parse_msgs = [], []
    prog = st.progress(0)
    for idx, uf in enumerate(uploaded_files):
        try:
            file_bytes = uf.read()
            df, msg = parse_file(file_bytes, uf.name)
            parse_msgs.append(f"**{uf.name}**: {msg}")
            if not df.empty:
                norm_df = normalize_dataframe(df)
                if not norm_df.empty:
                    all_dfs.append(norm_df)
                    parse_msgs.append(f"  → {len(norm_df)} {L('file_parsed')}")
        except Exception as e:
            parse_msgs.append(f"**{uf.name}**: ❌ {str(e)}")
        prog.progress((idx+1)/len(uploaded_files))

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        papers = compute_properties(df_to_papers(combined))
        st.session_state.papers = papers
        st.session_state.stats = compute_stats(papers)
        st.session_state.data_loaded = True
        st.session_state.raw_df = combined
        st.session_state.parse_log = parse_msgs
        st.rerun()
    else:
        st.session_state.parse_log = parse_msgs

# Parse log
if st.session_state.parse_log:
    with st.expander("📋 Parse Log", expanded=True):
        for msg in st.session_state.parse_log:
            st.markdown(msg)

# Data preview
if st.session_state.data_loaded:
    st.markdown("---")
    stats = st.session_state.stats
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric(L("paper_count"), stats.get("total_papers",0))
    c2.metric(L("total_citations"), f"{stats.get('total_citations',0):,}")
    c3.metric(L("year_range"), f"{stats.get('year_min','?')}–{stats.get('year_max','?')}")
    c4.metric("◉ Black Holes", stats.get("blackholes",0))
    c5.metric("⬡ Dyson", stats.get("dyson_spheres",0))

    st.markdown(f"### {L('top_papers')}")
    top = stats.get("top_5", [])
    if top:
        df_top = pd.DataFrame([{
            "Title": p.title[:60], "Authors": p.authors[:30], "Year": p.year,
            "Cites": p.cited_by_count, "Module": p.module,
            "Type": ("🕳️" if p.is_blackhole else "⬡" if p.is_dyson else "●"),
        } for p in top])
        st.dataframe(df_top, use_container_width=True, hide_index=True)

    # Module breakdown
    mods = stats.get("modules", {})
    if mods:
        st.markdown("### Module Distribution")
        mod_df = pd.DataFrame([{"Module": k, "Papers": v} for k, v in mods.items()])
        st.bar_chart(mod_df.set_index("Module")["Papers"])

    # arXiv batch import
    st.markdown("---")
    st.markdown(f"### 📡 {L('batch_import')}")
    ac1, ac2 = st.columns([3, 1])
    with ac1:
        arxiv_query = st.text_input("arXiv/OpenAlex query", placeholder="e.g. transformer attention mechanism", key="arxiv_q")
    with ac2:
        arxiv_n = st.number_input("Max papers", 5, 200, 20, key="arxiv_n")

    if arxiv_query and st.button(f"🚀 {L('arxiv_import')}", key="arxiv_btn"):
        with st.spinner(f"Fetching from arXiv: {arxiv_query}..."):
            try:
                import arxiv
                prog = st.progress(0)
                client = arxiv.Client()
                search = arxiv.Search(query=arxiv_query, max_results=arxiv_n, sort_by=arxiv.SortCriterion.Relevance)
                new_papers = []
                results = list(client.results(search))
                for i, r in enumerate(results):
                    new_papers.append({
                        "title": r.title, "authors": ", ".join([a.name for a in r.authors][:3]),
                        "year": r.published.year if r.published else 2024,
                        "abstract": (r.summary or "")[:500],
                        "doi": str(r.doi or ""), "keywords": ", ".join(r.categories),
                        "cited_by_count": 0, "module": "Other",
                    })
                    prog.progress((i+1)/len(results))
                if new_papers:
                    new_df = pd.DataFrame(new_papers)
                    new_p = compute_properties(df_to_papers(new_df))
                    st.session_state.papers.extend(new_p)
                    st.session_state.stats = compute_stats(st.session_state.papers)
                    st.success(f"✓ Added {len(new_papers)} papers from arXiv")
                    st.rerun()
            except ImportError:
                st.error("Install `arxiv` package: pip install arxiv")
            except Exception as e:
                st.error(f"arXiv error: {e}")

    st.markdown("""<div class="info-bar" style="margin-top:16px;">
        👈 Navigate to Universe, Analysis, or Timeline from the sidebar.
    </div>""", unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div style="text-align:center;padding:50px 20px;">
        <div style="font-size:64px;margin-bottom:16px;filter:drop-shadow(0 0 20px rgba(110,168,254,0.3));">🌌</div>
        <h2 style="margin-bottom:8px;background:linear-gradient(135deg,#6ea8fe,#b39ddb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:28px;">{L('welcome_title')}</h2>
        <p style="color:#8b8b94;font-size:14px;max-width:420px;margin:0 auto;line-height:1.7;">
            {L('welcome_sub')}<br><br>
            <span style="font-size:11px;color:#55555e;letter-spacing:0.5px;">
            CSV · JSON · XLSX · PDF · TXT · MD · DOCX · DOC · BibTeX
            </span>
        </p>
        <div style="margin-top:24px;display:flex;justify-content:center;gap:12px;flex-wrap:wrap;">
            <span style="background:rgba(110,168,254,0.08);border:1px solid rgba(110,168,254,0.15);border-radius:20px;padding:4px 14px;font-size:11px;color:#6ea8fe;">3D Universe</span>
            <span style="background:rgba(117,217,160,0.08);border:1px solid rgba(117,217,160,0.15);border-radius:20px;padding:4px 14px;font-size:11px;color:#75d9a0;">AI Analysis</span>
            <span style="background:rgba(179,157,219,0.08);border:1px solid rgba(179,157,219,0.15);border-radius:20px;padding:4px 14px;font-size:11px;color:#b39ddb;">Node Labels</span>
            <span style="background:rgba(253,214,99,0.08);border:1px solid rgba(253,214,99,0.15);border-radius:20px;padding:4px 14px;font-size:11px;color:#fdd663;">Gravity Grid</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
