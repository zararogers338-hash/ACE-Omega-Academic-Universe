# Architecture / 架构说明

## English

ACE-Omega is organized as a local Streamlit application with shared utility modules and multi-page visualization views.

```text
app.py                    Main home page, upload workflow, sidebar controls
pages/                    Streamlit multi-page views
utils/file_parser.py      Multi-format academic file parser
utils/data_processor.py   Paper dataclass, normalization output conversion, celestial properties
utils/components.py       Three.js HTML/JS components, session save/load, AI widgets
utils/ace_model.py        OpenAI / Ollama / GGUF / fallback inference layer
utils/i18n.py             English / Chinese text table
utils/theme.py            Streamlit CSS theme
```

The data flow is:

```text
Uploaded file / demo / arXiv query
        -> parse_file()
        -> normalize_dataframe()
        -> df_to_papers()
        -> compute_properties()
        -> Streamlit session_state
        -> 3D visualization pages + AI analysis
```

## 中文

ACE-Omega 是一个本地 Streamlit 应用，核心由主页、多个可视化页面和若干工具模块组成。

数据流是：上传文献文件、演示数据或 arXiv 查询进入解析器；解析器将数据整理成统一 DataFrame；数据处理模块把每条记录转成 Paper 对象，并计算质量、半径、位置、黑洞、戴森球等天体属性；最后由 Streamlit 页面和 Three.js 组件渲染成可交互学术宇宙。
