# Zero Data Egress Test Plan

Run these tests before using real work or customer data.

1. External URL blocked: `python -m unittest tests.test_security_guard.SecurityGuardTests.test_urllib_runtime_guard_blocks_external_url_before_network`.
2. Local Ollama allowed: `scripts\test-egress.ps1` should reach `http://127.0.0.1:11434` after Ollama starts.
3. OpenAI API key ignored: set `OPENAI_API_KEY` and verify `python app\security_status.py` reports only the variable name, not its value.
4. Remote embedding blocked: set a non-local embedding URL in config and verify `python app\security_status.py` fails.
5. Remote OCR blocked: OCR integrations must call `assert_zero_egress` and must not reference Google Vision, Azure Vision, AWS Textract, or online OCR APIs.
6. Mobile scan does not call internet: run `python app\mobile_app_review.py --file mobile\samples\example.apk --no-llm` and confirm no outbound network tool is used.
7. Folder watcher fails closed: watcher mode must not start unless zero-egress, firewall guard, local Ollama, and local endpoints pass.
8. Open WebUI local only: `podman ps` should show `127.0.0.1:3000->8080`, not `0.0.0.0`.
9. Python outbound blocked: run `scripts\enable-zero-egress.ps1`, then `scripts\test-egress.ps1`.
10. Reports stored locally: verify outputs are under `reports/` or `mobile/reports/`.
11. Logs do not contain secrets: inspect `logs/security_audit.log` and confirm API key values are not present.
12. Work and personal data not mixed: ingest/ask commands require explicit `--scope work` or `--scope personal`.
