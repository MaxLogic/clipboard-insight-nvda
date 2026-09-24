"""NVDA+C must not freeze NVDA, and the add-on must not change shared Windows API prototypes."""
import builtins
import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import threading
import time
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / "addon/globalPlugins/clipboardInsight.py"
sys.path.insert(0, str(ROOT / "addon/lib"))


class _Callback(object):
	def __init__(self, callback, name=None):
		self.callback = callback


class PluginTests(unittest.TestCase):
	def speak(self, sequence):
		# NVDA's speech: the text, then a callback it runs when speech reaches it.
		self.sequences.append(sequence)
		self.spoke.set()

	def reached(self):
		"""Speech got to the end of the last block, so NVDA runs its callback."""
		callbacks = [item for item in self.sequences[-1] if isinstance(item, _Callback)]
		self.assertEqual(len(callbacks), 1, "the block asks for no next block")
		callbacks[0].callback()

	def setUp(self):
		self.sequences = []
		self.spoken = []
		self.spoke = threading.Event()
		self.clipboard = ""

		def message(text):
			self.spoken.append(text)
			self.spoke.set()

		class _Base(object):
			pass

		boundary = {
			"addonHandler": types.SimpleNamespace(initTranslation=lambda: None),
			"api": types.SimpleNamespace(getClipData=lambda: self.clipboard),
			"globalPluginHandler": types.SimpleNamespace(GlobalPlugin=_Base),
			"scriptHandler": types.SimpleNamespace(
				script=lambda **kwargs: (lambda fn: fn),
				getLastScriptRepeatCount=lambda: 0,
			),
			"speech": types.SimpleNamespace(speakSpelling=lambda *args, **kwargs: None, speak=self.speak),
			"speech.commands": types.SimpleNamespace(CallbackCommand=_Callback),
			"ui": types.SimpleNamespace(message=message),
			# Stands in for NVDA's main thread, which runs queued functions in order.
			"queueHandler": types.SimpleNamespace(eventQueue="events", queueFunction=lambda queue, fn, *args: fn(*args)),
		}
		for patcher in (patch.dict(sys.modules, boundary), patch.object(builtins, "_", lambda text: text, create=True)):
			patcher.start()
			self.addCleanup(patcher.stop)
		spec = importlib.util.spec_from_file_location("clipboard_insight_under_test", PLUGIN_PATH)
		self.module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(self.module)
		self.plugin = self.module.GlobalPlugin()

	def test_counting_a_large_clipboard_does_not_freeze_nvda(self):
		self.clipboard = "word " * 400

		def slow_report(text, repeat_count):
			time.sleep(0.5)  # Loading the tokenizer takes about 1.3 s on first use.
			return "counted"

		with patch.object(self.module, "report_text", slow_report):
			started = time.perf_counter()
			self.plugin.script_reportClipboardText(None)
			self.assertLess(time.perf_counter() - started, 0.2, "NVDA waited for the token count")
			self.assertTrue(self.spoke.wait(3))
		self.assertEqual(self.spoken, ["counted"])

	def test_only_the_latest_press_is_reported(self):
		self.clipboard = "first text"
		release = threading.Event()

		def report(text, repeat_count):
			if text == "first text":
				release.wait(3)
			return text

		with patch.object(self.module, "report_text", report):
			self.plugin.script_reportClipboardText(None)
			self.clipboard = "second text"
			self.plugin.script_reportClipboardText(None)
			self.assertTrue(self.spoke.wait(3))
			release.set()
			time.sleep(0.2)
		self.assertEqual(self.spoken, ["second text"])

	def test_a_long_text_is_read_in_blocks_one_after_another(self):
		message = "".join("Line %d of a long clipboard text.\n" % n for n in range(2000))
		self.plugin._speakIfLatest(self.plugin._latestRequest, message)
		self.assertEqual(self.spoken, [], "the long text went to NVDA as one message")
		while any(isinstance(item, _Callback) for item in self.sequences[-1]):
			self.reached()
		texts = [item for sequence in self.sequences for item in sequence if isinstance(item, str)]
		self.assertEqual("".join(texts), message)
		self.assertGreater(len(texts), 10)
		self.assertTrue(all(len(text) <= self.module.READ_BLOCK_CHARS for text in texts))

	def test_cancelled_reading_stops_and_a_newer_press_does_not_resume_it(self):
		message = "word " * 5000
		self.plugin._speakIfLatest(self.plugin._latestRequest, message)
		self.reached()
		self.assertEqual(len(self.sequences), 2)
		# NVDA drops the callbacks of cancelled speech, so nothing more is read after Control.
		# A late callback from an older reading must not continue it either.
		self.plugin._latestRequest += 1
		self.reached()
		self.assertEqual(len(self.sequences), 2, "an old reading continued after a newer press")

	def test_a_short_report_is_one_message(self):
		self.plugin._speakIfLatest(self.plugin._latestRequest, "Hello. 1 word")
		self.assertEqual(self.spoken, ["Hello. 1 word"])
		self.assertEqual(self.sequences, [])

	def test_report_failure_is_announced_and_the_next_request_can_succeed(self):
		with patch.object(self.module, "report_text", side_effect=RuntimeError("analysis failed")):
			self.plugin._reportInBackground("text", 0)
			self.assertTrue(self.spoke.wait(3), "analysis failed without feedback")
		self.assertEqual(self.spoken, ["Could not analyze the clipboard. Press NVDA+c to try again."])
		self.spoke.clear()
		with patch.object(self.module, "report_text", return_value="recovered"):
			self.plugin._reportInBackground("text", 0)
			self.assertTrue(self.spoke.wait(3))
		self.assertEqual(self.spoken[-1], "recovered")

	def test_unloading_the_plugin_suppresses_queued_reports_and_reading(self):
		request = self.plugin._latestRequest
		self.plugin.terminate()
		self.plugin._speakIfLatest(request, "old report")
		self.plugin._readBlocks(request, ["old block"], 0)
		self.assertEqual(self.spoken, [])
		self.assertEqual(self.sequences, [])


@unittest.skipUnless(os.name == "nt", "Windows clipboard")
class SharedPrototypeTests(unittest.TestCase):
	def test_reading_clipboard_files_leaves_shared_prototypes_alone(self):
		from clipboardInsightLib.windows_clipboard import get_clipboard_files
		functions = (ctypes.windll.user32.GetClipboardData, ctypes.windll.user32.OpenClipboard, ctypes.windll.shell32.DragQueryFileW)
		before = [(function.argtypes, function.restype) for function in functions]
		get_clipboard_files()
		after = [(function.argtypes, function.restype) for function in functions]
		self.assertEqual(after, before, "the add-on changed ctypes.windll functions that NVDA and other add-ons share")


if __name__ == "__main__":
	unittest.main()
