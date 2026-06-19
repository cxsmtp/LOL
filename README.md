# local-ai-workbench

A practical, local-first AI workspace for a Windows 11 laptop. It uses Ollama for local inference, optional Open WebUI for chat via Podman, Python utilities for document Q&A/RAG and data analysis, and strict `work` vs `personal` folders so knowledge bases do not mix.

## First 30 minutes setup

1. Install Ollama from <https://ollama.com/download>.
2. Optional: install Podman Desktop if you want Open WebUI at `http://localhost:3000`.
3. Open PowerShell in this folder.
4. Run:

```powershell
scripts\install.ps1
scripts\pull-model.ps1 -ModelName llama3.2:3b
scripts\pull-model.ps1 -ModelName nomic-embed-text
scripts\start.ps1
scripts\healthcheck.ps1
```

If PowerShell blocks scripts, run this only for the current shell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Daily commands

```powershell
scripts\start.ps1        # start Ollama and optional Open WebUI via Podman
scripts\stop.ps1         # stop Open WebUI container
scripts\healthcheck.ps1  # check local services
ollama list              # list local models
```

## Model strategy

Edit `config/models.yaml` instead of hard-coding model names. Suggested categories are included for fast general chat, better reasoning, coding, and lightweight tasks. For 32GB RAM without a dedicated NVIDIA GPU, start with small/medium quantized models around 3B-8B parameters. Larger models may work but will be slower and may run out of memory.

Switch models by editing `default_chat_model` or by passing `--model` to scripts that support it. Pull a new model with:

```powershell
scripts\pull-model.ps1 -ModelName <ollama-model-name>
```

## Local chat

- Browser UI: run `scripts\start.ps1`, then open `http://localhost:3000`.
- Direct CLI: `ollama run llama3.2:3b`.
- Health check: `scripts\healthcheck.ps1` confirms Ollama API access.

## Work and personal separation

Use only these scopes:

- `work`: `data/work/inbox`, `data/work/processed`, `data/work/vector_store`
- `personal`: `data/personal/inbox`, `data/personal/processed`, `data/personal/vector_store`

The Python tools require `--scope work` or `--scope personal` and store vector data under that scope only.

## Document Q&A / RAG

Supported formats where dependencies can parse them: PDF, DOCX, TXT, MD, CSV, XLSX.

```powershell
# Ingest work documents
.\.venv\Scripts\python.exe app\ingest_documents.py --scope work

# Rebuild work vector store from scratch
.\.venv\Scripts\python.exe app\ingest_documents.py --scope work --rebuild

# Ingest personal documents
.\.venv\Scripts\python.exe app\ingest_documents.py --scope personal

# Ask work documents
.\.venv\Scripts\python.exe app\ask_documents.py --scope work --question "What are the key risks?"

# Ask personal documents
.\.venv\Scripts\python.exe app\ask_documents.py --scope personal --question "What appointments are mentioned?"
```

**Confidentiality warning:** do not ingest confidential customer or company data unless your company policy approves local AI processing on this laptop.

To delete a vector store, remove `data/<scope>/vector_store` or run ingestion with `--rebuild`.

## Presentation support

Prompt templates live in `prompts/`. Generate Markdown you can paste into PowerPoint:

```powershell
.\.venv\Scripts\python.exe app\generate_presentation_outline.py --input notes.md --output reports\storyline.md
```

This creates a 5-slide storyline, slide titles, talking points, speaker notes, customer-facing messaging, and a follow-up email. Future enhancement: generate `.pptx` files.

## Data analysis

Analyze local CSV/XLSX files without uploading data:

```powershell
.\.venv\Scripts\python.exe app\analyze_csv.py --scope work --file data\work\inbox\example.csv
```

Outputs are saved under `reports/<scope>/<file-name>/`, including a data profile CSV, charts, and an optional local-LLM executive summary.

## Mobile application testing support

The workbench includes a local static review helper for Android APK and iOS IPA files. It does not upload app binaries and does not perform dynamic testing, device testing, bypassing, or exploitation. Only test apps you own or are authorized to assess.

```powershell
# APK static review
.\.venv\Scripts\python.exe app\mobile_app_review.py --file mobile\samples\example.apk

# IPA static review
.\.venv\Scripts\python.exe app\mobile_app_review.py --file mobile\samples\example.ipa --no-llm
```

Reports are saved under `mobile/reports/`. For deeper APK metadata, install Android SDK build tools so `aapt` is available in PATH. IPA review extracts safe metadata from `Payload/*.app/Info.plist` when present.

## Optional automation

See `automation/README.md` and `automation/n8n_optional_notes.md`. Automation is intentionally optional and separate. Keep n8n bound to localhost and pass explicit `--scope` values.

## Minimal test plan

Run after setup:

```powershell
scripts\healthcheck.ps1
.\.venv\Scripts\python.exe -m py_compile app\utils.py app\ingest_documents.py app\ask_documents.py app\analyze_csv.py app\generate_presentation_outline.py
ollama list
```

Then test end-to-end with a small non-confidential `.txt` file in `data/personal/inbox`.

## Future improvements

- Add a small GUI launcher.
- Add optional PPTX generation.
- Add folder watcher mode.
- Add OCR for scanned PDFs.
- Add per-project workspaces inside `work` and `personal`.
- Add backup/restore scripts for vector stores and reports.

## Zero Data Egress Mode

Zero-egress mode is enabled by default in `config/security.yaml`. It allows only `localhost` and `127.0.0.1` on approved local ports and blocks external URLs from Python runtime calls where practical.

**Important warning:** Zero-egress mode reduces the risk of data leaving the laptop by enforcing local-only configuration, blocking external URLs, and adding firewall controls. It does not protect against malware, compromised operating system components, user-approved uploads, browser activity outside this tool, or manually copying data into cloud services.

What it protects:
- Prompts, documents, extracted text, embeddings, reports, mobile scan findings, and vector data used by this project.
- Local Ollama calls to `http://127.0.0.1:11434` or `http://localhost:11434`.
- Open WebUI bound to localhost through Podman.

What is blocked:
- External LLMs, hosted embeddings, cloud OCR, remote vector databases, web search, plugin marketplaces, external mobile scanning services, telemetry, analytics, and runtime package/model downloads.

Core commands:

```powershell
python app\security_status.py
scripts\enable-zero-egress.ps1
scripts\test-egress.ps1
scripts\disable-zero-egress.ps1
scripts\purge-local-data.ps1 -Reports
```

Temporarily disable zero-egress only during a controlled setup/update window. Do not use real customer/work data while Codex or any cloud coding assistant is building or modifying this project.

## GUI Launcher

A simple laptop-friendly Tkinter launcher is available:

```powershell
python app\gui_launcher.py
```

It shows the current security posture:
- ZERO-EGRESS MODE: ON / OFF
- Firewall Guard: ON / OFF or unknown
- External URLs: BLOCKED / ALLOWED
- Cloud APIs: BLOCKED / ALLOWED
- Ollama Binding expectation

If zero-egress mode is OFF, the GUI warns before opening work or personal folders.

## Automated Tests

Run local automated checks with:

```powershell
python -m py_compile app\*.py
python -m unittest discover -s tests -v
python app\security_status.py
```

These tests cover zero-egress URL blocking, environment API-key detection/redaction, APK fallback scanning, and IPA metadata extraction.
