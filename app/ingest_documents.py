from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import pandas as pd
from docx import Document
from pypdf import PdfReader
import chromadb
from utils import require_scope, scope_dir, vector_dir, check_ollama, ollama_embed, rebuild_vector_store

def read_file(path: Path) -> str:
    ext=path.suffix.lower()
    if ext in {".txt", ".md"}: return path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf": return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    if ext == ".docx": return "\n".join(p.text for p in Document(str(path)).paragraphs)
    if ext == ".csv": return pd.read_csv(path).to_csv(index=False)
    if ext in {".xlsx", ".xls"}: return pd.read_excel(path, sheet_name=None).__repr__()
    raise ValueError(f"Unsupported file type: {ext}")

def chunks(text: str, size=900, overlap=120):
    text=" ".join(text.split())
    step=max(1,size-overlap)
    for i in range(0,len(text),step):
        c=text[i:i+size]
        if c: yield c

def main():
    ap=argparse.ArgumentParser(description="Ingest local documents into a scope-specific vector store.")
    ap.add_argument("--scope", required=True, choices=["work","personal"])
    ap.add_argument("--rebuild", action="store_true", help="Delete and rebuild this scope's vector store.")
    args=ap.parse_args(); require_scope(args.scope)
    print("WARNING: Keep confidential data local and follow company policy before ingesting customer/work documents.")
    if not check_ollama(): raise SystemExit("Ollama is not reachable. Run scripts/start.ps1 and pull the embedding model.")
    if args.rebuild: rebuild_vector_store(args.scope)
    client=chromadb.PersistentClient(path=str(vector_dir(args.scope)))
    col=client.get_or_create_collection(f"{args.scope}_documents")
    inbox=scope_dir(args.scope)/"inbox"
    files=[p for p in inbox.iterdir() if p.is_file() and p.name != ".gitkeep"]
    if not files: print(f"No files found in {inbox}"); return
    for path in files:
        try: text=read_file(path)
        except Exception as e: print(f"Could not read {path.name}: {e}"); continue
        docs=list(chunks(text)); ids=[hashlib.sha256(f"{path}:{i}:{d[:30]}".encode()).hexdigest() for i,d in enumerate(docs)]
        embs=ollama_embed(docs)
        col.upsert(ids=ids, documents=docs, embeddings=embs, metadatas=[{"source":path.name,"scope":args.scope} for _ in docs])
        print(f"Ingested {path.name}: {len(docs)} chunks into {args.scope} store")
if __name__ == "__main__": main()
