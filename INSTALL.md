# Installation / 安装

## English

ACE-Omega Academic Universe is a local Streamlit application. The core app runs on CPU. AI analysis is optional and depends on your chosen backend.

### 1. Clone

```bash
git clone https://github.com/zararogers338-hash/ACE-Omega-Academic-Universe.git
cd ACE-Omega-Academic-Universe
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
streamlit run app.py
```

Open `http://localhost:8501`.

### Optional AI backends

- OpenAI-compatible API: configure API key in the sidebar.
- Ollama: install Ollama, run `ollama serve`, then choose an installed model.
- GGUF: install a compatible local inference stack such as `llama-cpp-python`, then upload or configure a `.gguf` model.

## 中文

ACE-Omega Academic Universe 是一个本地 Streamlit 应用。核心可视化功能可以只用 CPU 运行。AI 分析是可选功能，取决于你配置的后端。

### 1. 克隆仓库

```bash
git clone https://github.com/zararogers338-hash/ACE-Omega-Academic-Universe.git
cd ACE-Omega-Academic-Universe
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动

```bash
streamlit run app.py
```

然后打开 `http://localhost:8501`。

### 可选 AI 后端

- OpenAI-compatible API：在侧边栏配置 API key；
- Ollama：安装 Ollama，运行 `ollama serve`，选择本地模型；
- GGUF：安装兼容的本地推理环境，例如 `llama-cpp-python`，然后上传或配置 `.gguf` 模型。
