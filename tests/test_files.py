import sys
import unittest
from ctypes import wintypes
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "addon" / "lib"))

from clipboardInsightLib.files import summarize_files
from clipboardInsightLib.windows_clipboard import CF_HDROP, _configure_clipboard_api


class DummyFunction:
	def __call__(self, *args):
		return 0


class DummyLibrary:
	def __init__(self, *names):
		for name in names:
			setattr(self, name, DummyFunction())


class FileSummaryTests(unittest.TestCase):
	def test_single_file_summary_includes_path_and_kind(self):
		summary = summarize_files([r"C:\Temp\report.pdf"])
		self.assertEqual(summary, r"1 file on the clipboard: C:\Temp\report.pdf, PDF file")

	def test_multiple_file_summary_limits_paths(self):
		summary = summarize_files(
			[
				r"C:\Temp\one.txt",
				r"C:\Temp\two.docx",
				r"C:\Temp\three.png",
				r"C:\Temp\four.zip",
			],
		)
		self.assertIn(r"C:\Temp\one.txt", summary)
		self.assertIn(r"C:\Temp\two.docx", summary)
		self.assertIn(r"C:\Temp\three.png", summary)
		self.assertNotIn(r"C:\Temp\four.zip", summary)
		self.assertIn("and 1 more", summary)

	def test_cf_hdrop_constant(self):
		self.assertEqual(CF_HDROP, 15)

	def test_clipboard_api_uses_pointer_safe_signatures(self):
		user32 = DummyLibrary("OpenClipboard", "IsClipboardFormatAvailable", "GetClipboardData", "CloseClipboard")
		shell32 = DummyLibrary("DragQueryFileW")
		_configure_clipboard_api(user32, shell32)
		self.assertIs(user32.GetClipboardData.restype, wintypes.HANDLE)
		self.assertIs(shell32.DragQueryFileW.argtypes[0], wintypes.HANDLE)


if __name__ == "__main__":
	unittest.main()
