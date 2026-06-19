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
