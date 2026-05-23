"""Test Groq parser with sample Hinglish enquiry (no Telegram or Sheets)."""

from __future__ import annotations

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Sample counselor input in Hinglish
SAMPLE_ENQUIRY = """
Aaj walk in aaya — student Rahul Sharma, class 9, Foundation course dekhna hai.
Papa ka naam Sunil Sharma, maa ne bataya school DPS Meerut hai.
Student mobile 9876543210, papa 9123456789.
Ladka hai, DOB 14 October 2010.
Address: 45 Civil Lines, Meerut.
Fees 85000 discuss ki, 10% sibling discount bola.
Kal follow up call karna hai papa ko.
Banner se aaye the mall ke paas wale.
"""

EXPECTED_KEYS = [
    "Date",
    "Student Name",
    "Parent Name",
    "Student Phone",
    "Parent Phone",
    "Class & Course",
    "Gender & DOB",
    "School",
    "Address",
    "Lead Source",
    "Counseling Notes",
    "Follow Up",
    "N/A",
]

MOCK_PARSED = {
    "Date": "21 May 2026",
    "Student Name": "Rahul Sharma",
    "Parent Name": "Sunil Sharma",
    "Student Phone": "9876543210",
    "Parent Phone": "9123456789",
    "Class & Course": "9 | Foundation",
    "Gender & DOB": "Male | 14 Oct 2010",
    "School": "DPS Meerut",
    "Address": "45 Civil Lines, Meerut",
    "Lead Source": "Banner",
    "Counseling Notes": "Fees 85000 discussed, 10% sibling discount mentioned",
    "Follow Up": "Call papa tomorrow",
    "N/A": "",
}


class TestParserHelpers(unittest.TestCase):
    def test_merge_prefers_non_empty(self):
        from parser import _empty_record, merge_parsed

        a = _empty_record()
        b = _empty_record()
        a["Student Name"] = "A"
        a["Counseling Notes"] = "fee 1"
        b["Parent Name"] = "B"
        b["Counseling Notes"] = "fee 2"

        merged = merge_parsed(a, b)
        self.assertEqual(merged["Student Name"], "A")
        self.assertEqual(merged["Parent Name"], "B")
        self.assertIn("fee 1", merged["Counseling Notes"])
        self.assertIn("fee 2", merged["Counseling Notes"])

    def test_normalize_empty_lead_source(self):
        from parser import _normalize_record

        record = _normalize_record({"Lead Source": "", "Student Name": "Test"})
        self.assertEqual(record["Lead Source"], "")
        self.assertEqual(record["Student Name"], "Test")

    def test_normalize_telecaller_alias(self):
        from parser import _normalize_lead_source

        self.assertEqual(_normalize_lead_source("telecaller team se call"), "Telecaller")
        self.assertEqual(_normalize_lead_source("Telecaller"), "Telecaller")

    def test_all_lead_sources_in_config(self):
        import config

        self.assertIn("Telecaller", config.LEAD_SOURCES)


class TestParserWithMock(unittest.TestCase):
    @patch("parser._client")
    def test_parse_text_returns_all_keys(self, mock_client_fn):
        from parser import parse_text

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(MOCK_PARSED)))
        ]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_client_fn.return_value = mock_client

        result = parse_text(SAMPLE_ENQUIRY)

        for key in EXPECTED_KEYS:
            self.assertIn(key, result)

        self.assertEqual(result["Student Name"], "Rahul Sharma")
        self.assertEqual(result["Class & Course"], "9 | Foundation")
        self.assertEqual(result["Lead Source"], "Banner")
        mock_client.chat.completions.create.assert_called_once()


class TestParserLive(unittest.TestCase):
    """Runs only when GROQ_API_KEY is set — hits real Groq API."""

    @unittest.skipUnless(
        os.getenv("GROQ_API_KEY"),
        "Set GROQ_API_KEY in .env to run live parser test",
    )
    def test_live_parse_hinglish_sample(self):
        from dotenv import load_dotenv

        load_dotenv()
        from parser import parse_text

        result = parse_text(SAMPLE_ENQUIRY)
        print("\n--- Live parse result ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        for key in EXPECTED_KEYS:
            self.assertIn(key, result)

        self.assertTrue(result["Student Name"], "Student name should be extracted")
        self.assertIn("Foundation", result["Class & Course"])


def run_mock_tests() -> bool:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestParserHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestParserWithMock))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    ok = run_mock_tests()
    if "--live" in sys.argv and os.getenv("GROQ_API_KEY"):
        unittest.main(argv=[sys.argv[0]], exit=False, verbosity=2)
    sys.exit(0 if ok else 1)
