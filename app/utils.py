from __future__ import annotations
import json, os, shutil
from pathlib import Path
from typing import Iterable
import requests, yaml

ROOT = Path(__file__).resolve().parents[1]
VALID_SCOPES = {"work", "personal"}

def load_yaml(path: str | Path) -> dict:
    with open(ROOT / path if not Path(path).is_absolute() else path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def require_scope(scope: str) -> str:
    if scope not in VALID_SCOPES:
        raise ValueError("Scope must be exactly 'work' or 'personal'. This prevents mixing data.")
    return scope

def scope_dir(scope: str) -> Path:
    return ROOT / "data" / require_scope(scope)

def vector_dir(scope: str) -> Path:
    p = scope_dir(scope) / "vector_store"
    p.mkdir(parents=True, exist_ok=True)
    return p

def ollama_base_url() -> str:
    return load_yaml("config/app_settings.yaml").get("ollama", {}).get("base_url", "http://localhost:11434")

def chat_model() -> str:
    return load_yaml("config/models.yaml").get("default_chat_model", "llama3.2:3b")

def embedding_model() -> str:
    return load_yaml("config/models.yaml").get("embedding_model", "nomic-embed-text")

def check_ollama() -> bool:
    try:
        requests.get(f"{ollama_base_url()}/api/tags", timeout=3).raise_for_status()
        return True
    except requests.RequestException:
        return False

def ollama_generate(prompt: str, model: str | None = None) -> str:
    r = requests.post(f"{ollama_base_url()}/api/generate", json={"model": model or chat_model(), "prompt": prompt, "stream": False}, timeout=300)
    r.raise_for_status()
    return r.json().get("response", "")

def ollama_embed(texts: Iterable[str], model: str | None = None) -> list[list[float]]:
    out=[]
    for text in texts:
        r=requests.post(f"{ollama_base_url()}/api/embeddings", json={"model": model or embedding_model(), "prompt": text}, timeout=120)
        r.raise_for_status(); out.append(r.json()["embedding"])
    return out

def rebuild_vector_store(scope: str) -> None:
    p = vector_dir(scope)
    shutil.rmtree(p, ignore_errors=True)
    p.mkdir(parents=True, exist_ok=True)
