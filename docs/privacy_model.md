# Privacy Model

## What stays local
Documents, vector stores, reports, prompts, and Ollama model calls stay on the laptop by default.

## What may leave the laptop
Data may leave only if you deliberately configure optional cloud services, external APIs, remote sync folders, or hosted automation.

## Separation
Use `data/work` for company material and `data/personal` for personal material. Scripts reject any scope except `work` or `personal` and store vector data under that scope only.

## Deletion
Delete `data/<scope>/vector_store` to remove local RAG indexes. Use `ollama list` and `ollama rm <model>` to remove models. Clear `reports/` if generated summaries contain sensitive data.

## Logs and prompts
Scripts print status messages to the console. Avoid saving sensitive prompts in shell history. Do not feed confidential customer data unless approved by company policy.

## Zero Data Egress Mode

Zero-egress mode is configured in `config/security.yaml` and defaults to ON. When enabled, only local hosts and approved ports are allowed. Python runtime guards block external `requests`, `urllib`, and `httpx` calls where practical, and security events are written to `logs/security_audit.log` without prompt contents, document contents, or secret values.

Important warning: Zero-egress mode reduces the risk of data leaving the laptop by enforcing local-only configuration, blocking external URLs, and adding firewall controls. It does not protect against malware, compromised operating system components, user-approved uploads, browser activity outside this tool, or manually copying data into cloud services.

Use `scripts\enable-zero-egress.ps1` to add Windows Defender Firewall rules for project executables and `scripts\test-egress.ps1` to verify external calls fail while localhost Ollama works.
