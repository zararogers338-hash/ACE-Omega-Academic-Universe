"""
ACE-Omega Unified Model Backend v3.1
Fixed: Ollama response parsing for all SDK versions.
"""
import json, time, logging, os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("ace_model")
ERROR_LOG = Path("./logs/model_errors.jsonl")
ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)

@dataclass
class ModelResponse:
    text: str = ""; backend: str = "unknown"; model_name: str = "unknown"
    latency_ms: float = 0.0; tokens_used: int = 0
    degraded: bool = False; error: Optional[str] = None

@dataclass
class BackendStatus:
    name: str; available: bool = False; error: Optional[str] = None
    models: list = field(default_factory=list); info: str = ""
    vram_mb: float = 0.0

def _extract_text(obj):
    """Robustly extract text from any response object (ollama, openai, etc)."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in ['content', 'text', 'response', 'message']:
            if k in obj:
                return _extract_text(obj[k])
        return str(obj)
    # ChatResponse / Message objects from ollama SDK
    if hasattr(obj, 'message'):
        msg = obj.message
        if hasattr(msg, 'content') and msg.content is not None:
            return str(msg.content)
        if isinstance(msg, dict):
            return msg.get('content', str(msg))
        return str(msg)
    for attr in ['content', 'text', 'response']:
        if hasattr(obj, attr):
            val = getattr(obj, attr)
            if val is not None:
                return _extract_text(val)
    return str(obj)

def check_gguf(config):
    s = BackendStatus(name="gguf")
    try:
        mp = config.get("gguf", {}).get("model_path", "")
        if not mp or not Path(mp).exists():
            s.error = f"No GGUF file at: {mp}"; return s
        from llama_cpp import Llama
        s.available = True; s.models = [Path(mp).name]
        fsize = Path(mp).stat().st_size / (1024*1024)
        s.info = f"{Path(mp).name} ({fsize:.0f}MB)"
        s.vram_mb = fsize * 0.6
    except ImportError: s.error = "llama-cpp-python not installed"
    except Exception as e: s.error = str(e)
    return s

def check_ollama(config):
    s = BackendStatus(name="ollama")
    try:
        import ollama as oll
        cfg = config.get("ollama", {})
        host = f"{cfg.get('host', 'http://localhost')}:{cfg.get('port', 11434)}"
        client = oll.Client(host=host)
        models = client.list()
        ml = []
        if hasattr(models, 'models'):
            ml = [str(getattr(m, 'model', getattr(m, 'name', str(m)))) for m in models.models]
        elif isinstance(models, dict) and 'models' in models:
            ml = [m.get('name', m.get('model', str(m))) for m in models['models']]
        s.available = True; s.models = ml; s.info = f"{len(ml)} models"
    except ImportError: s.error = "ollama not installed"
    except Exception as e: s.error = str(e)
    return s

def check_openai(config):
    s = BackendStatus(name="openai")
    try:
        from openai import OpenAI
        cfg = config.get("openai", {})
        if not cfg.get("api_key"):
            s.error = "No API key"; return s
        s.available = True; s.models = [cfg.get("model", "gpt-4o-mini")]
        s.info = f"Model: {cfg.get('model', 'gpt-4o-mini')}"
    except ImportError: s.error = "openai not installed"
    except Exception as e: s.error = str(e)
    return s

def ollama_list_models(config):
    try:
        import ollama as oll
        cfg = config.get("ollama", {})
        host = f"{cfg.get('host', 'http://localhost')}:{cfg.get('port', 11434)}"
        client = oll.Client(host=host)
        models = client.list()
        ml = []
        if hasattr(models, 'models'):
            ml = [str(getattr(m, 'model', getattr(m, 'name', str(m)))) for m in models.models]
        elif isinstance(models, dict) and 'models' in models:
            ml = [m.get('name', m.get('model', str(m))) for m in models['models']]
        return ml, None
    except Exception as e:
        return [], str(e)

def ollama_pull_model(config, model_name, progress_callback=None):
    try:
        import ollama as oll
        cfg = config.get("ollama", {})
        host = f"{cfg.get('host', 'http://localhost')}:{cfg.get('port', 11434)}"
        client = oll.Client(host=host)
        for progress in client.pull(model_name, stream=True):
            if progress_callback:
                if isinstance(progress, dict):
                    status = progress.get('status', '')
                    total = progress.get('total', 0)
                    completed = progress.get('completed', 0)
                    pct = completed / total if total > 0 else 0
                    progress_callback(status, pct)
                elif hasattr(progress, 'status'):
                    total = getattr(progress, 'total', 0) or 0
                    completed = getattr(progress, 'completed', 0) or 0
                    pct = completed / total if total > 0 else 0
                    progress_callback(str(progress.status), pct)
        return True, None
    except Exception as e:
        return False, str(e)

def load_gguf_from_upload(file_bytes, filename):
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    path = models_dir / filename
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)

def infer_gguf(prompt, config, system=""):
    start = time.time()
    try:
        from llama_cpp import Llama
        cfg = config.get("gguf", {})
        llm = Llama(model_path=cfg["model_path"], n_ctx=cfg.get("n_ctx", 16384),
                     n_gpu_layers=cfg.get("n_gpu_layers", -1), verbose=False)
        out = llm(prompt, max_tokens=cfg.get("max_tokens", 4096), temperature=cfg.get("temperature", 0.3))
        txt = out["choices"][0]["text"]; lat = (time.time()-start)*1000
        return ModelResponse(text=txt, backend="gguf", model_name=Path(cfg["model_path"]).name, latency_ms=lat)
    except Exception as e:
        return ModelResponse(error=str(e), backend="gguf", degraded=True)

def infer_ollama(prompt, config, system=""):
    start = time.time()
    try:
        import ollama as oll
        cfg = config.get("ollama", {})
        client = oll.Client(host=f"{cfg.get('host','http://localhost')}:{cfg.get('port',11434)}")
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        r = client.chat(model=cfg.get("model", "llama3"), messages=msgs, stream=False)
        txt = _extract_text(r)
        return ModelResponse(text=txt, backend="ollama", model_name=cfg.get("model", ""), latency_ms=(time.time()-start)*1000)
    except Exception as e:
        return ModelResponse(error=str(e), backend="ollama", degraded=True)

def infer_openai(prompt, config, system=""):
    start = time.time()
    try:
        from openai import OpenAI
        cfg = config.get("openai", {})
        client = OpenAI(api_key=cfg.get("api_key", ""), base_url=cfg.get("base_url", "https://api.openai.com/v1"),
                        timeout=cfg.get("timeout", 60))
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        r = client.chat.completions.create(model=cfg.get("model", "gpt-4o-mini"), messages=msgs,
                                            max_tokens=cfg.get("max_tokens", 4096), temperature=cfg.get("temperature", 0.3))
        txt = r.choices[0].message.content or ""
        return ModelResponse(text=txt, backend="openai", model_name=cfg.get("model", ""),
                             latency_ms=(time.time()-start)*1000, tokens_used=getattr(r.usage, 'total_tokens', 0) if r.usage else 0)
    except Exception as e:
        return ModelResponse(error=str(e), backend="openai", degraded=True)

def infer_fallback(prompt, config, system=""):
    return ModelResponse(text=f"[Fallback] AI unavailable. Input: {len(prompt.split())} words.",
                         backend="fallback", model_name="rules", degraded=True, latency_ms=1)

def infer(prompt, config, system=""):
    active = config.get("active_backend", "openai")
    chains = {"gguf": [infer_gguf, infer_ollama, infer_openai, infer_fallback],
              "ollama": [infer_ollama, infer_openai, infer_fallback],
              "openai": [infer_openai, infer_fallback], "fallback": [infer_fallback]}
    for fn in chains.get(active, [infer_openai, infer_fallback]):
        try:
            r = fn(prompt, config, system)
            if r.error is None: return r
        except: continue
    return infer_fallback(prompt, config)

def health_check(config):
    r = infer("Say 'OK' in one word.", config)
    return r

def check_all_backends(config):
    return {"gguf": check_gguf(config), "ollama": check_ollama(config), "openai": check_openai(config)}
