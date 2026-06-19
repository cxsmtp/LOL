from __future__ import annotations
import argparse, json, plistlib, shutil, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from security_guard import assert_zero_egress, audit_event

SUSPICIOUS_ANDROID_PERMISSIONS = [
    "READ_SMS", "SEND_SMS", "RECEIVE_SMS", "READ_CONTACTS", "RECORD_AUDIO",
    "CAMERA", "ACCESS_FINE_LOCATION", "READ_CALL_LOG", "WRITE_SETTINGS",
]

def zip_summary(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        total = sum(i.file_size for i in zf.infolist())
        return {
            "file_count": len(names),
            "uncompressed_bytes": total,
            "top_level_entries": sorted({n.split("/")[0] for n in names if n})[:50],
            "interesting_files": [n for n in names if any(x in n.lower() for x in ["manifest", "plist", "privacy", "firebase", "google-services", "entitlements"])][:100],
        }

def scan_zip_for_terms(path: Path, terms: list[str]) -> list[str]:
    """Best-effort scan of small text-like archive entries for terms.

    APK manifests are commonly binary XML, so this does not replace Android
    build tools. It still helps with test fixtures and archives containing
    plain-text metadata.
    """
    found: set[str] = set()
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.file_size > 2_000_000 or info.is_dir():
                continue
            try:
                data = zf.read(info.filename).decode("utf-8", errors="ignore")
            except Exception:
                continue
            upper = data.upper()
            for term in terms:
                if term.upper() in upper:
                    found.add(term)
    return sorted(found)

def run_if_available(command: list[str]) -> tuple[bool, str]:
    if not shutil.which(command[0]):
        return False, f"{command[0]} not found"
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, (result.stdout or result.stderr).strip()
    except Exception as exc:
        return False, str(exc)

def analyze_apk(path: Path) -> dict:
    report = {"type": "apk", "path": str(path), "zip": zip_summary(path), "tool_outputs": {}}
    ok, output = run_if_available(["aapt", "dump", "badging", str(path)])
    report["tool_outputs"]["aapt_badging"] = {"available": ok, "output": output[:12000]}
    if ok:
        report["package_hint"] = next((line for line in output.splitlines() if line.startswith("package:")), "")
        report["permission_findings"] = [p for p in SUSPICIOUS_ANDROID_PERMISSIONS if p in output]
    else:
        report["permission_findings"] = scan_zip_for_terms(path, SUSPICIOUS_ANDROID_PERMISSIONS)
        report["note"] = "Install Android build tools for deeper APK metadata: aapt or apkanalyzer. Fallback ZIP text scanning is best-effort only."
    return report

def analyze_ipa(path: Path) -> dict:
    report = {"type": "ipa", "path": str(path), "zip": zip_summary(path), "info_plist": {}, "embedded_profiles": []}
    with zipfile.ZipFile(path) as zf:
        plist_names = [n for n in zf.namelist() if n.startswith("Payload/") and n.endswith(".app/Info.plist")]
        if plist_names:
            with zf.open(plist_names[0]) as f:
                info = plistlib.load(f)
            keys = ["CFBundleIdentifier", "CFBundleName", "CFBundleDisplayName", "CFBundleShortVersionString", "CFBundleVersion", "MinimumOSVersion", "UIDeviceFamily", "NSCameraUsageDescription", "NSLocationWhenInUseUsageDescription", "NSMicrophoneUsageDescription"]
            report["info_plist"] = {k: info.get(k) for k in keys if k in info}
        report["embedded_profiles"] = [n for n in zf.namelist() if n.endswith("embedded.mobileprovision")]
    return report

def llm_summary(report: dict, model: str | None) -> str:
    from utils import ollama_generate
    prompt = """You are a mobile application testing assistant. Review this static local APK/IPA report.
Explain what was found, likely risks, and next manual tests. Do not claim dynamic testing was performed.
Keep work/personal/customer data local and remind the user to follow authorization policies.

Report JSON:
""" + json.dumps(report, indent=2)[:20000]
    return ollama_generate(prompt, model)

def main() -> None:
    parser = argparse.ArgumentParser(description="Create a local static review report for APK or IPA files.")
    parser.add_argument("--file", required=True, help="Path to .apk or .ipa")
    parser.add_argument("--output", help="Markdown report path. Defaults to mobile/reports/<file>.md")
    parser.add_argument("--json-output", help="Optional JSON report path")
    parser.add_argument("--model", help="Optional Ollama model for summary")
    parser.add_argument("--no-llm", action="store_true", help="Skip local LLM summary")
    args = parser.parse_args()
    assert_zero_egress("mobile_app_review", "mobile_static_scan")
    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".apk":
        report = analyze_apk(path)
    elif suffix == ".ipa":
        report = analyze_ipa(path)
    else:
        raise SystemExit("Only .apk and .ipa files are supported.")
    out = Path(args.output) if args.output else ROOT / "mobile" / "reports" / f"{path.stem}_mobile_review.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    json_out = Path(args.json_output) if args.json_output else out.with_suffix(".json")
    json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = "Local LLM summary skipped or Ollama not reachable.\n"
    if not args.no_llm:
        try:
            from utils import check_ollama
            if check_ollama():
                summary = llm_summary(report, args.model)
        except Exception as exc:
            summary = f"Local LLM summary unavailable: {exc}\n"
    markdown = f"# Mobile App Static Review: {path.name}\n\n> Local static review only. Do not test apps you do not own or lack permission to assess.\n\n## Summary\n\n{summary}\n\n## Raw Findings\n\n```json\n{json.dumps(report, indent=2)}\n```\n"
    out.write_text(markdown, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Wrote {json_out}")

if __name__ == "__main__":
    main()
