from __future__ import annotations
import argparse
import chromadb
from utils import require_scope, vector_dir, check_ollama, ollama_embed, ollama_generate, chat_model
from security_guard import assert_zero_egress

def main():
    ap=argparse.ArgumentParser(description="Ask questions over a local work or personal document store.")
    ap.add_argument("--scope", required=True, choices=["work","personal"]); ap.add_argument("--question", required=True); ap.add_argument("--model")
    args=ap.parse_args(); require_scope(args.scope)
    assert_zero_egress("ask_documents", "rag_query")
    if not check_ollama(): raise SystemExit("Ollama is not reachable. Run scripts/start.ps1")
    col=chromadb.PersistentClient(path=str(vector_dir(args.scope))).get_or_create_collection(f"{args.scope}_documents")
    qemb=ollama_embed([args.question])[0]
    res=col.query(query_embeddings=[qemb], n_results=5)
    docs=res.get("documents", [[]])[0]; metas=res.get("metadatas", [[]])[0]
    if not docs: raise SystemExit(f"No documents found for {args.scope}. Run ingestion first.")
    context="\n\n".join(f"Source: {m.get('source')}\n{d}" for d,m in zip(docs,metas))
    prompt=f"Answer using only this {args.scope} context. If unsure, say what is missing.\n\n{context}\n\nQuestion: {args.question}"
    print(ollama_generate(prompt, args.model or chat_model()))
if __name__ == "__main__": main()
