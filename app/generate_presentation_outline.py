from __future__ import annotations
import argparse
from pathlib import Path
from utils import ollama_generate, check_ollama, ROOT
from security_guard import assert_zero_egress

def main():
    ap=argparse.ArgumentParser(description="Turn rough notes into a Markdown presentation outline.")
    ap.add_argument("--input", required=True); ap.add_argument("--output", default="reports/presentation_outline.md"); ap.add_argument("--model")
    args=ap.parse_args(); inp=Path(args.input)
    assert_zero_egress("generate_presentation_outline", "presentation_generation")
    if not inp.exists(): raise SystemExit(f"Input not found: {inp}")
    notes=inp.read_text(encoding="utf-8", errors="ignore")
    prompt=(ROOT/"prompts"/"presentation_assistant.md").read_text(encoding="utf-8")+f"\n\nCreate a 5-slide executive storyline with slide titles, talking points, speaker notes, customer-facing messaging, and follow-up email.\n\nRaw notes:\n{notes}"
    output=Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    if not check_ollama(): raise SystemExit("Ollama is not reachable. Run scripts/start.ps1")
    output.write_text(ollama_generate(prompt,args.model), encoding="utf-8")
    print(f"Wrote {output}")
if __name__ == "__main__": main()
