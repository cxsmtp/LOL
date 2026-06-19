# Operating Guide

1. Put documents in `data/work/inbox` or `data/personal/inbox`.
2. Run `python app/ingest_documents.py --scope work` or `--scope personal`.
3. Ask with `python app/ask_documents.py --scope work --question "What are the key risks?"`.
4. Analyze data with `python app/analyze_csv.py --file data/work/inbox/file.csv --scope work`.
5. Generate presentation outlines with `python app/generate_presentation_outline.py --input notes.md --output reports/storyline.md`.

## Zero Data Egress Operating Steps

1. Run `python app\security_status.py` before processing files.
2. Start with `scripts\start.ps1`; it runs security checks and sets `OLLAMA_HOST=127.0.0.1:11434`.
3. Run `scripts\enable-zero-egress.ps1` to add project firewall block rules.
4. Run `scripts\test-egress.ps1` to confirm external network fails and local Ollama works.
5. If zero-egress is OFF, do not process work/customer documents.
6. Use `scripts\purge-local-data.ps1` to delete local reports, logs, vector stores, caches, and mobile scan reports.
