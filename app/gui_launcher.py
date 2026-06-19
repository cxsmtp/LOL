from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from security_guard import print_security_status, scan_config_for_external_endpoints, scan_env_for_api_keys, security_config, zero_egress_enabled

ROOT = Path(__file__).resolve().parents[1]
THEME_BG = "#0f172a"
PANEL_BG = "#1e293b"
TEXT = "#e2e8f0"
ACCENT = "#38bdf8"
WARN = "#f59e0b"
OK = "#22c55e"
BAD = "#ef4444"

class LocalAIWorkbench(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Local AI Workbench")
        self.geometry("760x520")
        self.configure(bg=THEME_BG)
        self.status = tk.StringVar()
        self._build()
        self.refresh_status()

    def _build(self) -> None:
        tk.Label(self, text="Local AI Workbench", fg=ACCENT, bg=THEME_BG, font=("Segoe UI", 22, "bold")).pack(pady=14)
        panel = tk.Frame(self, bg=PANEL_BG, padx=16, pady=16)
        panel.pack(fill="x", padx=18)
        self.status_label = tk.Label(panel, textvariable=self.status, fg=TEXT, bg=PANEL_BG, justify="left", font=("Consolas", 11))
        self.status_label.pack(anchor="w")
        buttons = tk.Frame(self, bg=THEME_BG)
        buttons.pack(fill="both", expand=True, padx=18, pady=16)
        for text, command in [
            ("Refresh Security Status", self.refresh_status),
            ("Open README", lambda: self.open_file(ROOT / "README.md")),
            ("Open Work Inbox", lambda: self.open_file(ROOT / "data" / "work" / "inbox")),
            ("Open Personal Inbox", lambda: self.open_file(ROOT / "data" / "personal" / "inbox")),
            ("Open Mobile Samples", lambda: self.open_file(ROOT / "mobile" / "samples")),
            ("Run Security Status in Console", self.console_status),
        ]:
            tk.Button(buttons, text=text, command=command, bg="#334155", fg=TEXT, activebackground=ACCENT, relief="flat", padx=12, pady=10).pack(fill="x", pady=5)
        tk.Label(self, text="Warning: if ZERO-EGRESS MODE is OFF, do not process work/customer documents.", fg=WARN, bg=THEME_BG).pack(pady=6)

    def refresh_status(self) -> None:
        cfg = security_config()
        problems = scan_config_for_external_endpoints(raise_on_error=False)
        keys = scan_env_for_api_keys()
        zero = zero_egress_enabled()
        self.status.set(
            f"ZERO-EGRESS MODE: {'ON' if zero else 'OFF'}\n"
            f"Firewall Guard: {('ON' if self._firewall_marker() else 'UNKNOWN/OFF')}\n"
            f"External URLs: {'BLOCKED' if not cfg.get('allow_external_urls') else 'ALLOWED'}\n"
            f"Cloud APIs: {'BLOCKED' if not cfg.get('allow_cloud_llm') else 'ALLOWED'}\n"
            f"Ollama Binding: LOCALHOST expected (127.0.0.1:11434)\n"
            f"Config findings: {len(problems)}\n"
            f"Cloud/API key env vars present but ignored: {', '.join(keys) if keys else 'none'}"
        )
        self.status_label.configure(fg=OK if zero and not problems else BAD)

    def _firewall_marker(self) -> bool:
        return (ROOT / "logs" / "zero_egress_firewall.enabled").exists()

    def console_status(self) -> None:
        print_security_status()
        messagebox.showinfo("Security Status", "Security status printed to the console.")

    def open_file(self, path: Path) -> None:
        if not zero_egress_enabled():
            messagebox.showwarning("Zero-egress is OFF", "Do not process work/customer documents until zero-egress mode is enabled.")
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

if __name__ == "__main__":
    LocalAIWorkbench().mainloop()
