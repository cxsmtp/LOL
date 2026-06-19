# Mobile App Testing Support

This folder is for authorized local APK/IPA review. Place sample binaries in `mobile/samples/` and write outputs to `mobile/reports/`.

The initial helper performs static archive inspection only:

- APK: ZIP structure, interesting files, optional `aapt dump badging` when Android build tools are installed.
- IPA: ZIP structure and `Payload/*.app/Info.plist` metadata extraction.
- Optional local Ollama summary of findings and next manual tests.

It does not perform dynamic testing, bypass controls, device interaction, exploitation, or cloud uploads. Only test mobile apps you own or have explicit permission to assess.

Example:

```powershell
.\.venv\Scripts\python.exe app\mobile_app_review.py --file mobile\samples\example.apk --no-llm
```
