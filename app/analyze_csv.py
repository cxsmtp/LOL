from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from utils import require_scope, ROOT, ollama_generate, check_ollama

def main():
    ap=argparse.ArgumentParser(description="Analyze a local CSV/XLSX and write local reports.")
    ap.add_argument("--file", required=True); ap.add_argument("--scope", required=True, choices=["work","personal"]); ap.add_argument("--model")
    args=ap.parse_args(); require_scope(args.scope)
    path=Path(args.file); 
    if not path.exists(): raise SystemExit(f"File not found: {path}")
    df=pd.read_excel(path) if path.suffix.lower() in {".xlsx",".xls"} else pd.read_csv(path)
    out=ROOT/"reports"/args.scope/path.stem; out.mkdir(parents=True, exist_ok=True)
    summary=df.describe(include="all").transpose(); missing=df.isna().sum().rename("missing_values")
    report=pd.concat([summary, missing], axis=1); report.to_csv(out/"data_profile.csv")
    numeric=df.select_dtypes("number")
    if not numeric.empty:
        numeric.hist(figsize=(10,8)); plt.tight_layout(); plt.savefig(out/"numeric_histograms.png"); plt.close()
    prompt=f"Explain these local {args.scope} data findings in business language. Do not assume data left the laptop.\nColumns: {list(df.columns)}\nRows: {len(df)}\nProfile:\n{report.head(30).to_string()}"
    if check_ollama(): (out/"executive_summary.md").write_text(ollama_generate(prompt,args.model), encoding="utf-8")
    else: (out/"executive_summary.md").write_text("Ollama not reachable; data_profile.csv was created locally.\n", encoding="utf-8")
    print(f"Saved local report to {out}")
if __name__ == "__main__": main()
