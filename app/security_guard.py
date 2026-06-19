from __future__ import annotations

import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import yaml
except Exception:  # pragma: no cover - install-time fallback
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SECURITY_CONFIG = ROOT / "config" / "security.yaml"
AUDIT_LOG = ROOT / "logs" / "security_audit.log"
SENSITIVE_ENV_NAMES = [
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
    "AZURE_OPENAI_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
    "HUGGINGFACE_TOKEN", "HF_TOKEN", "LANGCHAIN_API_KEY", "LANGSMITH_API_KEY",
    "SERPAPI_API_KEY", "TAVILY_API_KEY", "OLLAMA_API_KEY",
]
EXTERNAL_PROVIDER_HINTS = [
    "openai", "anthropic", "google", "gemini", "azure", "aws", "huggingface",
    "cohere", "voyage", "serpapi", "tavily", "virustotal", "github.com",
]
_local_hosts = {"localhost", "127.0.0.1", "::1"}
_PATCHED = False

class ZeroEgressViolation(RuntimeError):
    """Raised when an action would violate zero-egress policy."""

def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    if yaml is None:
        # Tiny fallback for this config shape only.
        data: dict[str, Any] = {}
        current_list: str | None = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-") and current_list:
                data.setdefault(current_list, []).append(line[1:].strip().strip('"'))
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip(); value = value.strip()
                if value == "":
                    current_list = key; data[key] = []
                elif value.lower() in {"true", "false"}:
                    data[key] = value.lower() == "true"; current_list = None
                elif value.isdigit():
                    data[key] = int(value); current_list = None
                else:
                    data[key] = value.strip('"'); current_list = None
        return data
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

def security_config() -> dict[str, Any]:
    defaults = {
        "zero_egress_mode": True,
        "allow_external_urls": False,
        "allow_cloud_llm": False,
        "allow_remote_embeddings": False,
        "allowed_hosts": ["127.0.0.1", "localhost"],
        "allowed_ports": [11434, 3000, 8080],
    }
    defaults.update(_load_yaml(SECURITY_CONFIG))
    return defaults

def zero_egress_enabled() -> bool:
    return bool(security_config().get("zero_egress_mode", True))

def redact_sensitive_values(value: Any) -> Any:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if any(token in key.upper() for token in ["KEY", "TOKEN", "SECRET", "PASSWORD"]):
                redacted[key] = "<redacted>"
            else:
                redacted[key] = redact_sensitive_values(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive_values(item) for item in value]
    return value

def audit_event(module: str, action: str, destination: str = "", blocked: bool = False, details: dict[str, Any] | None = None) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    safe_details = redact_sensitive_values(details or {})
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "zero_egress_mode": zero_egress_enabled(),
        "module": module,
        "action": action,
        "destination": destination,
        "blocked": blocked,
        "firewall_mode": os.environ.get("LOCAL_AI_FIREWALL_GUARD", "unknown"),
        "details": safe_details,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")

def validate_url_is_local(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ZeroEgressViolation(f"Unsupported or non-local URL scheme: {parsed.scheme or '<none>'}")
    host = (parsed.hostname or "").lower()
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    cfg = security_config()
    allowed_hosts = {str(h).lower() for h in cfg.get("allowed_hosts", [])}
    allowed_ports = {int(p) for p in cfg.get("allowed_ports", [])}
    if host not in allowed_hosts or port not in allowed_ports:
        raise ZeroEgressViolation(f"Blocked external URL in zero-egress mode: {host}:{port}")
    return True

def block_external_url(url: str, module: str = "unknown") -> None:
    if zero_egress_enabled():
        try:
            validate_url_is_local(url)
        except ZeroEgressViolation:
            audit_event(module, "blocked_external_url", url, blocked=True)
            raise

def assert_zero_egress(module: str = "unknown", action: str = "security_check") -> None:
    cfg = security_config()
    if not cfg.get("zero_egress_mode", True):
        audit_event(module, action, blocked=False, details={"warning": "zero egress disabled"})
        return
    problems = []
    for key in ["allow_network", "allow_cloud_llm", "allow_remote_embeddings", "allow_telemetry", "allow_auto_update", "allow_external_urls"]:
        if cfg.get(key) is True:
            problems.append(f"{key} must be false")
    external = scan_config_for_external_endpoints(raise_on_error=False)
    if external:
        problems.extend(external)
    if problems:
        audit_event(module, action, blocked=True, details={"problems": problems})
        raise ZeroEgressViolation("Zero-egress checks failed: " + "; ".join(problems))
    audit_event(module, action, blocked=False)

def scan_config_for_external_endpoints(raise_on_error: bool = True) -> list[str]:
    problems: list[str] = []
    for path in (ROOT / "config").glob("*.yaml"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in ["http://", "https://"]:
            start = 0
            while True:
                idx = text.find(token, start)
                if idx == -1:
                    break
                end_candidates = [text.find(ch, idx) for ch in ['"', "'", "\n", " "] if text.find(ch, idx) != -1]
                end = min(end_candidates) if end_candidates else len(text)
                url = text[idx:end].strip()
                try:
                    validate_url_is_local(url)
                except ZeroEgressViolation as exc:
                    problems.append(f"{path.relative_to(ROOT)} contains external endpoint {url}: {exc}")
                start = idx + len(token)
        lower = text.lower()
        for hint in EXTERNAL_PROVIDER_HINTS:
            if hint in lower and "localhost" not in lower:
                problems.append(f"{path.relative_to(ROOT)} references possible external provider: {hint}")
    if problems and raise_on_error:
        raise ZeroEgressViolation("External endpoint configuration blocked: " + "; ".join(problems))
    return problems

def scan_env_for_api_keys() -> list[str]:
    found = [name for name in SENSITIVE_ENV_NAMES if os.environ.get(name)]
    if found:
        audit_event("security_guard", "api_key_environment_detected", blocked=False, details={"keys_present": found})
    return found

def print_security_status() -> None:
    cfg = security_config()
    env_keys = scan_env_for_api_keys()
    config_problems = scan_config_for_external_endpoints(raise_on_error=False)
    print("ZERO-EGRESS MODE:", "ON" if cfg.get("zero_egress_mode") else "OFF")
    print("External URLs:", "BLOCKED" if not cfg.get("allow_external_urls") else "ALLOWED")
    print("Cloud APIs:", "BLOCKED" if not cfg.get("allow_cloud_llm") else "ALLOWED")
    print("Remote embeddings:", "BLOCKED" if not cfg.get("allow_remote_embeddings") else "ALLOWED")
    print("Allowed hosts:", ", ".join(map(str, cfg.get("allowed_hosts", []))))
    print("Allowed ports:", ", ".join(map(str, cfg.get("allowed_ports", []))))
    print("API key environment variables present:", ", ".join(env_keys) if env_keys else "none")
    print("External config findings:", "; ".join(config_problems) if config_problems else "none")

def install_runtime_network_guard() -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True
    if not zero_egress_enabled():
        return
    try:
        import requests
        original_request = requests.sessions.Session.request
        def guarded_request(self, method, url, *args, **kwargs):
            block_external_url(str(url), module="requests")
            return original_request(self, method, url, *args, **kwargs)
        requests.sessions.Session.request = guarded_request
    except Exception:
        pass
    try:
        import urllib.request
        original_urlopen = urllib.request.urlopen
        def guarded_urlopen(url, *args, **kwargs):
            target = getattr(url, "full_url", url)
            block_external_url(str(target), module="urllib")
            return original_urlopen(url, *args, **kwargs)
        urllib.request.urlopen = guarded_urlopen
    except Exception:
        pass
    try:
        import httpx
        original_httpx_request = httpx.Client.request
        def guarded_httpx_request(self, method, url, *args, **kwargs):
            block_external_url(str(url), module="httpx")
            return original_httpx_request(self, method, url, *args, **kwargs)
        httpx.Client.request = guarded_httpx_request
    except Exception:
        pass

install_runtime_network_guard()
