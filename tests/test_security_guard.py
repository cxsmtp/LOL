from __future__ import annotations

import os
import sys
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from security_guard import (  # noqa: E402
    ZeroEgressViolation,
    redact_sensitive_values,
    scan_env_for_api_keys,
    validate_url_is_local,
)


class SecurityGuardTests(unittest.TestCase):
    def test_validate_url_allows_local_ollama(self) -> None:
        self.assertTrue(validate_url_is_local("http://127.0.0.1:11434/api/tags"))
        self.assertTrue(validate_url_is_local("http://localhost:3000"))

    def test_validate_url_blocks_external_url(self) -> None:
        with self.assertRaises(ZeroEgressViolation):
            validate_url_is_local("https://example.com")

    def test_urllib_runtime_guard_blocks_external_url_before_network(self) -> None:
        with self.assertRaises(ZeroEgressViolation):
            urllib.request.urlopen("https://example.com", timeout=1)

    def test_scan_env_for_api_keys_reports_names_not_values(self) -> None:
        old = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "super-secret-value"
        try:
            found = scan_env_for_api_keys()
        finally:
            if old is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = old
        self.assertIn("OPENAI_API_KEY", found)

    def test_redact_sensitive_values(self) -> None:
        data = {"api_key": "secret", "nested": {"token": "secret2", "safe": "ok"}}
        self.assertEqual(redact_sensitive_values(data)["api_key"], "<redacted>")
        self.assertEqual(redact_sensitive_values(data)["nested"]["token"], "<redacted>")
        self.assertEqual(redact_sensitive_values(data)["nested"]["safe"], "ok")


if __name__ == "__main__":
    unittest.main()
