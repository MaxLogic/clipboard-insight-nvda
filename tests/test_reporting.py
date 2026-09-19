import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "addon" / "lib"))

from clipboardInsightLib.reporting import report_text, split_for_reading


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


class ReadingBlockTests(unittest.TestCase):
	def test_blocks_are_short_and_rebuild_the_text(self):
		text = "".join("Line %d says a few words about the weather. It goes on.\n" % n for n in range(400))
		blocks = split_for_reading(text, 500)
		self.assertEqual("".join(blocks), text)
		self.assertTrue(all(0 < len(block) <= 500 for block in blocks))
		# Blocks end at line breaks when there are any.
		self.assertTrue(all(block.endswith("\n") for block in blocks[:-1]))

	def test_a_long_line_splits_at_a_sentence_end_or_a_space(self):
		text = "This is one sentence among many. " * 100
		blocks = split_for_reading(text, 300)
		self.assertEqual("".join(blocks), text)
		self.assertTrue(all(block.endswith(". ") for block in blocks[:-1]))
		words = "word " * 200
		self.assertTrue(all(block.endswith(" ") for block in split_for_reading(words, 97)[:-1]))

	def test_text_without_spaces_is_cut_at_the_limit(self):
		blocks = split_for_reading("x" * 1000, 300)
		self.assertEqual([len(block) for block in blocks], [300, 300, 300, 100])

	def test_short_text_is_one_block(self):
		self.assertEqual(split_for_reading("Short.", 300), ["Short."])


if __name__ == "__main__":
	unittest.main()
