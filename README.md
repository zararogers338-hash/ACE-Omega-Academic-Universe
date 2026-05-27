# 🌌 ACE-Omega Academic Universe

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)
![Visualization](https://img.shields.io/badge/Visualization-Three.js-purple.svg)
![Status](https://img.shields.io/badge/Status-Open%20Source%20Preview-brightgreen.svg)

**ACE-Omega Academic Universe** is an open-source Streamlit and Three.js platform that transforms scattered academic literature into an interactive celestial system. Papers become stars, highly cited works become black holes or Dyson spheres, research fields become clusters, and the evolution of knowledge can be explored through timeline replay, gravity-grid visualization, AI analysis, and cosmic metaphors.

**ACE-Omega 学术宇宙** 是一个基于 Streamlit 与 Three.js 的开源学术文献可视化平台。它把散乱的论文、文献、引用和研究主题转化为一个可以交互探索的“学术天体系统”：论文是星体，高引用论文是黑洞或戴森球，研究方向是星团，知识演化可以通过时间线、引力网格、AI 分析和宇宙隐喻来观察。

> The core idea: make an academic field visible as a universe.  
> 核心思想：把一个学术领域变成可以被看见、被探索、被追问的宇宙。

---

## What is this? / 这是什么？

ACE-Omega is not a normal chart dashboard. It is a cross-disciplinary research interface that uses astronomy, network thinking, bibliometrics, data visualization, and AI-assisted interpretation to help users observe academic corpora.

ACE-Omega 不是普通图表面板，而是一个跨学科研究界面。它把天文学隐喻、网络科学、文献计量、数据可视化和 AI 辅助解释结合起来，让用户用“宇宙结构”的方式观察一个学术领域。

It can ingest literature files, normalize inconsistent metadata, compute visual properties for each paper, and render the dataset as an interactive 3D universe.

它可以导入文献数据，自动整理不一致的字段，计算每篇论文的“天体属性”，并把整个数据集渲染成一个可交互的 3D 学术宇宙。

---

## Key Features / 核心功能

- **Universal literature import**: CSV, JSON, XLSX, PDF, TXT, Markdown, DOCX, DOC, BibTeX, RIS, XML, HTML and more.
- **Intelligent field normalization**: maps inconsistent columns such as title, authors, year, citations and abstract into a standard schema.
- **Academic celestial mapping**: papers become celestial bodies; citations influence mass, radius and height.
- **Black hole detection**: foundational or extremely cited papers are marked as black holes.
- **Dyson sphere detection**: dominant high-impact works are marked as paradigm-capturing structures.
- **Gravity grid visualization**: displays a warped research-space metaphor around influential papers.
- **Satellite rings and asteroid belts**: visual metaphors for follow-up clusters and scattered low-impact fragments.
- **Timeline replay**: explore how a field evolves by year.
- **Observer collapse mode**: interactively reveal papers from an unknown corpus.
- **Global search and highlighting**: search papers across the loaded universe.
- **AI analysis**: ask questions about patterns, gaps, anomalies and paradigm shifts.
- **Multiple AI backends**: OpenAI-compatible APIs, Ollama, GGUF / llama.cpp-style local models, and rule-based fallback.
- **Session save/load**: export and reload analysis states.
- **Bilingual UI**: English and Chinese interface.

中文概括：

- 支持多种文献文件导入；
- 自动标准化论文标题、作者、年份、引用、摘要等字段；
- 把论文映射为 3D 天体；
- 用引用量和排名识别“黑洞论文”和“戴森球论文”；
- 用引力网格、卫星环、小行星带等隐喻表现学术结构；
- 支持时间线回放、全局搜索、观察者坍缩、AI 解读和会话保存；
- 支持 OpenAI-compatible API、Ollama、本地 GGUF 模型和规则兜底。

---

## Why this matters / 为什么这个项目有意义？

Traditional literature review tools often show tables, keyword clouds or citation charts. ACE-Omega tries a different path: it turns a research field into a spatial system. Instead of only reading lists of papers, users can observe where influential works cluster, where new fields emerge, where attention collapses around a few papers, and where the structure becomes noisy or fragmented.

传统文献综述工具通常展示表格、关键词云或引用图。ACE-Omega 走的是另一条路：它把研究领域变成一个空间系统。用户不只是读论文列表，而是观察哪些论文形成引力中心，哪些方向正在出现，注意力是否坍缩到少数论文，领域结构是否变得嘈杂、碎片化或异常集中。

This is especially useful for:

- literature mapping;
- research trend exploration;
- academic field overview;
- interdisciplinary topic discovery;
- teaching bibliometrics and research methodology;
- AI-assisted systematic review prototyping;
- building visual research maps for papers, theses or reports.

它适合用于：

- 文献地图构建；
- 研究趋势探索；
- 学术领域概览；
- 跨学科主题发现；
- 文献计量与研究方法教学；
- AI 辅助系统综述原型；
- 论文、课题、报告中的可视化研究地图。

---

## Installation / 安装

Recommended Python version: **Python 3.10 or Python 3.11**.

推荐使用：**Python 3.10 或 Python 3.11**。

```bash
git clone https://github.com/zararogers338-hash/ACE-Omega-Academic-Universe.git
cd ACE-Omega-Academic-Universe
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

You can also use:

```bat
launch.bat
```

or:

```bash
bash launch.sh
```

---

## Quick Start / 快速开始

1. Start the app with `streamlit run app.py`.
2. Open the local web page.
3. Click **Load Demo** to generate a synthetic academic universe.
4. Or upload your own literature file.
5. Explore pages such as Universe Overview, Celestial Bodies, Gravity Grid, Black Holes, Dyson Spheres and Timeline.
6. Configure an AI backend if you want natural-language analysis.

中文：

1. 使用 `streamlit run app.py` 启动应用；
2. 打开本地网页；
3. 点击 **Load Demo** 生成演示学术宇宙；
4. 或者上传自己的文献文件；
5. 在 Universe Overview、Celestial Bodies、Gravity Grid、Black Holes、Dyson Spheres、Timeline 等页面中探索；
6. 如果需要自然语言分析，可以配置 AI 后端。

---

## Data Schema / 数据格式

ACE-Omega tries to normalize many different input schemas into these standard fields:

| Field | Meaning |
|---|---|
| `title` | Paper title |
| `authors` | Authors |
| `year` | Publication year |
| `cited_by_count` | Citation count |
| `abstract` | Abstract or description |
| `keywords` | Keywords |
| `doi` | DOI or identifier |
| `module` | Research field / category |
| `journal` | Journal, venue or source |

The app can still work if some fields are missing. Missing citation counts default to `0`, missing authors default to `Unknown`, and missing modules default to `Other`.

即使字段不完整，系统也会尽量运行。缺失引用量会默认为 `0`，缺失作者会默认为 `Unknown`，缺失领域会默认为 `Other`。

---

## Celestial Metaphor / 天体隐喻

| Academic concept | Celestial metaphor | Meaning |
|---|---|---|
| Paper | Celestial body / star | A single research work |
| Citation count | Mass / radius / height | Influence and visibility |
| High-impact paper | Black hole | A foundational gravity center |
| Dominant paradigm paper | Dyson sphere | A work that captures a large field of attention |
| Follow-up cluster | Satellite ring | Papers orbiting an influential core |
| Fragmented low-impact works | Asteroid belt | Scattered fragments in the literature space |
| Research field | Module / constellation | A disciplinary or topical cluster |
| Timeline | Cosmic expansion | Evolution of the field over time |

中文理解：

论文不是表格里的死数据，而是一个知识宇宙中的天体。引用量越高，它的质量、半径和引力越强；少数极高影响力论文会像黑洞一样改变周围结构；一些主导范式的论文会像戴森球一样吸收大量注意力；低引用、分散的主题像小行星带；不同学科方向形成不同星团。

---

## AI Backends / AI 后端

ACE-Omega supports four backend modes:

1. **OpenAI-compatible API** - for cloud or compatible API servers.
2. **Ollama** - for local models served by Ollama.
3. **GGUF / llama.cpp-style local model** - for local model files.
4. **Fallback** - rule-based mode when no AI backend is available.

The visualization and data processing features do **not** require AI. AI is only needed for natural-language interpretation.

可视化和数据处理功能不强制依赖 AI。AI 后端主要用于自然语言分析与解释。

---

## Project Status / 项目状态

This is an **open-source preview release**. The core parsing, normalization, demo generation, celestial property computation and Streamlit pages are included. Advanced AI behavior depends on your local model setup, API keys, Ollama installation or GGUF runtime.

这是一个 **开源预览版本**。核心的文件解析、字段标准化、演示数据生成、天体属性计算和 Streamlit 页面已经包含。高级 AI 分析能力取决于你的本地模型、API key、Ollama 或 GGUF 运行环境。

---

## Important Notes / 重要说明

- This project is for research visualization, education and exploratory analysis.
- It is **not** a source of absolute bibliometric truth.
- Citation counts may be incomplete or missing depending on your data source.
- AI answers may be wrong; verify important claims manually.
- Do not commit API keys or private literature datasets.
- Do not expose the Streamlit app to untrusted networks without authentication.

中文：

- 本项目用于研究可视化、教学和探索性分析；
- 它不是绝对准确的文献计量裁判；
- 引用量取决于输入数据来源，可能缺失或不完整；
- AI 回答可能出错，重要结论需要人工核查；
- 不要提交 API key 或私有文献数据；
- 不要在没有访问控制的情况下把 Streamlit 应用暴露到不可信网络。

---

## Documentation / 文档

- [Installation Guide](INSTALL.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Methodology](docs/METHODOLOGY.md)
- [Data Formats](docs/DATA_FORMATS.md)
- [AI Backends](docs/AI_BACKENDS.md)
- [Visualization Metaphor](docs/VISUALIZATION_METAPHOR.md)
- [Safety Notes](docs/SAFETY.md)
- [Roadmap](docs/ROADMAP.md)
- [Original Technical Manual PDF](docs/ACE_Omega_Manual.pdf)

---

## License / 许可证

This project is released under the MIT License. See [LICENSE](LICENSE).

本项目使用 MIT License 开源。详见 [LICENSE](LICENSE)。
