# ACE-Omega Academic Universe v4.0 Open Source Preview

ACE-Omega Academic Universe is an open-source Streamlit and Three.js platform that transforms academic literature into an interactive 3D celestial system.

ACE-Omega 学术宇宙是一个基于 Streamlit 和 Three.js 的开源平台，用来把学术文献转化为可交互的 3D 学术天体系统。

## English

This is the first open-source preview release of **ACE-Omega Academic Universe v4.0**.

The project treats an academic corpus as a universe. Papers become celestial bodies, citation counts influence mass and radius, highly cited works can become black holes or Dyson spheres, research fields become clusters, and the evolution of knowledge can be explored through timeline replay, gravity-grid visualization and AI-assisted analysis.

It is designed for literature mapping, bibliometric exploration, research trend observation, interdisciplinary discovery, teaching, and experimental AI-assisted research workflows.

## 中文

这是 **ACE-Omega Academic Universe v4.0** 的第一个开源预览版本。

本项目把学术文献集合看作一个宇宙：论文成为天体，引用量影响质量和半径，高影响力论文可能成为黑洞或戴森球，研究领域形成星团，知识演化可以通过时间线回放、引力网格可视化和 AI 辅助分析来观察。

它适合用于文献地图、文献计量探索、研究趋势观察、跨学科发现、教学，以及实验性的 AI 辅助研究工作流。

## Included in this release / 本版本包含

- Streamlit local web interface
- Three.js-based interactive 3D universe visualization
- Multi-page academic celestial views
- CSV / JSON / XLSX / PDF / TXT / Markdown / DOCX / BibTeX parsing
- Intelligent metadata normalization
- Paper-to-celestial-body computation
- Black hole and Dyson sphere detection
- Gravity grid, satellite ring, asteroid belt and timeline metaphors
- Global search and label display
- AI analysis with OpenAI-compatible API, Ollama, GGUF and fallback modes
- Session save/load
- Bilingual English / Chinese interface
- Example datasets
- Technical manual PDF
- Bilingual documentation
- Self-check and smoke-test scripts
- Open-source cleanup

## Installation / 安装

```bash
git clone https://github.com/zararogers338-hash/ACE-Omega-Academic-Universe.git
cd ACE-Omega-Academic-Universe
pip install -r requirements.txt
streamlit run app.py
```

Windows users can also run:

```bat
launch.bat
```

Linux/macOS users can run:

```bash
bash launch.sh
```

## Important Notice / 重要说明

ACE-Omega is a research visualization and exploration tool. It is not an absolute judge of academic quality or scientific truth.

ACE-Omega 是研究可视化和探索工具，不是判断学术质量或科学真理的绝对裁判。

Citation counts may be incomplete, AI interpretation may be wrong, and important claims should be verified manually.

引用数据可能不完整，AI 解读可能出错，重要结论需要人工核查。

## Project Status / 项目状态

This is an open-source preview release. It is suitable for exploration, testing, education and research prototypes. Advanced AI functions depend on the user's API keys, Ollama setup, local model files or GGUF runtime.

这是一个开源预览版本，适合探索、测试、教学和研究原型。高级 AI 功能取决于用户自己的 API key、Ollama、本地模型文件或 GGUF 运行环境。
