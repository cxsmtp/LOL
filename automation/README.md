# Optional Automation
Automation is optional and local-first. Start manually before adding watchers.

Examples:
- Summarize a local meeting transcript with `python app/ask_documents.py --scope work --question "Summarize the latest transcript"` after ingestion.
- Convert notes into action items using `prompts/meeting_summary.md`.
- Analyze a spreadsheet with `python app/analyze_csv.py --file data/work/inbox/example.xlsx --scope work`.
- Watch folders manually by placing files in `data/<scope>/inbox` and running ingestion on demand.
