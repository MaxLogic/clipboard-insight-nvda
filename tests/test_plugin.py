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


class PluginTests(unittest.TestCase):
	def setUp(self):
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
			"speech": types.SimpleNamespace(speakSpelling=lambda *args, **kwargs: None),
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
