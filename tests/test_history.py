import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "addon" / "globalPlugins"))

from clipboardInsightLib.history import ClipboardHistory


class HistoryTests(unittest.TestCase):
	def test_deduplicates_consecutive_items(self):
		history = ClipboardHistory()
		history.add("text", "one", "one")
		history.add("text", "one", "one")
		self.assertEqual(len(history.items), 1)

	def test_previous_and_next_navigation(self):
		history = ClipboardHistory()
		history.add("text", "one", "one")
		history.add("text", "two", "two")
		history.add("files", "3 files", "a|b|c")
		self.assertEqual(history.previous().summary, "two")
		self.assertEqual(history.previous().summary, "one")
		self.assertEqual(history.next().summary, "two")


if __name__ == "__main__":
	unittest.main()
