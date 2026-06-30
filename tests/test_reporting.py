import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "addon" / "globalPlugins"))

from clipboardInsightLib.reporting import report_text


class ReportingTests(unittest.TestCase):
	def test_empty_text_report(self):
		self.assertEqual(report_text("", repeat_count=0), "There is no text or file content on the clipboard")
		self.assertEqual(report_text("   ", repeat_count=0), "There is no text or file content on the clipboard")

	def test_short_text_first_press_includes_metrics(self):
		report = report_text("Hello world", repeat_count=0)
		self.assertIn("Hello world", report)
		self.assertIn("11 characters", report)
		self.assertIn("2 words", report)
		self.assertIn("2 tokens", report)

	def test_short_text_repeat_modes(self):
		self.assertEqual(report_text("Hello", repeat_count=1), "SPELL:Hello")
		self.assertEqual(report_text("Hello", repeat_count=2), "CHAR_DESC:Hello")

	def test_long_text_first_press_reports_metrics_without_full_text(self):
		text = "word " * 300
		report = report_text(text, repeat_count=0)
		self.assertIn("The clipboard contains a large amount of text", report)
		self.assertIn("1500 characters", report)
		self.assertIn("300 words", report)
		self.assertNotIn(text, report)

	def test_long_text_second_press_reads_text_with_metrics(self):
		text = "word " * 300
		report = report_text(text, repeat_count=1)
		self.assertIn(text, report)
		self.assertIn("1500 characters", report)
		self.assertIn("300 words", report)


if __name__ == "__main__":
	unittest.main()
