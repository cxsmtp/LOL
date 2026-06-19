from __future__ import annotations

import io
import plistlib
import sys
import zipfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from mobile_app_review import analyze_apk, analyze_ipa  # noqa: E402


class MobileAppReviewTests(unittest.TestCase):
    def test_analyze_apk_fallback_finds_plain_text_permissions(self) -> None:
        path = Path("/tmp/local-ai-workbench-test.apk")
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "AndroidManifest.xml",
                '<manifest><uses-permission android:name="android.permission.CAMERA" /></manifest>',
            )

        report = analyze_apk(path)

        self.assertEqual(report["type"], "apk")
        self.assertIn("AndroidManifest.xml", report["zip"]["interesting_files"])
        self.assertIn("CAMERA", report["permission_findings"])

    def test_analyze_ipa_extracts_info_plist(self) -> None:
        path = Path("/tmp/local-ai-workbench-test.ipa")
        plist_bytes = io.BytesIO()
        plistlib.dump(
            {
                "CFBundleIdentifier": "com.example.local",
                "CFBundleName": "LocalExample",
                "CFBundleShortVersionString": "1.2.3",
            },
            plist_bytes,
        )
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("Payload/LocalExample.app/Info.plist", plist_bytes.getvalue())

        report = analyze_ipa(path)

        self.assertEqual(report["type"], "ipa")
        self.assertEqual(report["info_plist"]["CFBundleIdentifier"], "com.example.local")
        self.assertEqual(report["info_plist"]["CFBundleName"], "LocalExample")


if __name__ == "__main__":
    unittest.main()
