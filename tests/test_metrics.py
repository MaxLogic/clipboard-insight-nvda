import sys
from unittest import mock
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "addon" / "lib"))

import tiktoken

from clipboardInsightLib.metrics import measure_text


class MetricsTests(unittest.TestCase):
	def test_counts_text_with_o200k_tokens(self):
		text = "Hello world\nagain"
		metrics = measure_text(text)
		expected_tokens = len(tiktoken.get_encoding("o200k_base").encode(text))
		self.assertTrue(Path(tiktoken.__file__).is_relative_to(ROOT / "addon" / "lib"))
		self.assertEqual(metrics.characters, len(text))
		self.assertEqual(metrics.words, 3)
		self.assertEqual(metrics.lines, 2)
		self.assertEqual(metrics.tokens, expected_tokens)
		self.assertFalse(metrics.tokens_estimated)

	def test_o200k_works_without_requests_or_cache(self):
		import tiktoken.registry

		tiktoken.registry.ENCODINGS.clear()
		tiktoken.registry.ENCODING_CONSTRUCTORS = None
		with (
			mock.patch.dict(sys.modules, {"requests": None}),
			mock.patch("tiktoken.load.read_file_cached", side_effect=AssertionError("cache should not be used")),
		):
			metrics = measure_text("offline tokens")
		self.assertFalse(metrics.tokens_estimated)
		self.assertGreater(metrics.tokens, 0)

	def test_special_token_literals_are_counted_as_text(self):
		metrics = measure_text("<|endoftext|>")
		self.assertFalse(metrics.tokens_estimated)
		self.assertGreater(metrics.tokens, 0)

	def test_fallback_is_marked_estimated_when_tokenizer_load_fails(self):
		with mock.patch("clipboardInsightLib.metrics._load_o200k_encoding", side_effect=ImportError):
			metrics = measure_text("fallback tokens")
		self.assertTrue(metrics.tokens_estimated)


if __name__ == "__main__":
	unittest.main()
