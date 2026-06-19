# Operating Guide

1. Put documents in `data/work/inbox` or `data/personal/inbox`.
2. Run `python app/ingest_documents.py --scope work` or `--scope personal`.
3. Ask with `python app/ask_documents.py --scope work --question "What are the key risks?"`.
4. Analyze data with `python app/analyze_csv.py --file data/work/inbox/file.csv --scope work`.
5. Generate presentation outlines with `python app/generate_presentation_outline.py --input notes.md --output reports/storyline.md`.
