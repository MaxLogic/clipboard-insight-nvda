from pathlib import Path
import sys

import addonHandler
import api
import globalPluginHandler
import scriptHandler
import speech
import ui


_LIB = Path(__file__).resolve().parents[1] / "lib"
if str(_LIB) not in sys.path:
	sys.path.insert(0, str(_LIB))

from clipboardInsightLib.reporting import LONG_TEXT_THRESHOLD, report_text
from clipboardInsightLib.files import summarize_files
from clipboardInsightLib.history import ClipboardHistory
from clipboardInsightLib.windows_clipboard import get_clipboard_files


addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Clipboard Insight")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._history = ClipboardHistory()

	@scriptHandler.script(
		description=_("Reports clipboard text with characters, words, and token count."),
		gesture="kb:NVDA+c",
	)
	def script_reportClipboardText(self, gesture):
		try:
			text = api.getClipData()
		except Exception:
			text = ""
		if not text or text.isspace():
			try:
				files = get_clipboard_files()
			except Exception:
				files = []
			if files:
				message = summarize_files(files)
				self._history.add("files", message, "\n".join(files))
				ui.message(message)
				return
		repeat_count = scriptHandler.getLastScriptRepeatCount()
		if text and not text.isspace() and repeat_count and len(text) < LONG_TEXT_THRESHOLD:
			speech.speakSpelling(text, useCharacterDescriptions=repeat_count > 1)
			return
		message = report_text(text, repeat_count)
		if text and not text.isspace():
			self._history.add("text", message, text)
		ui.message(message)

	@scriptHandler.script(
		description=_("Reports the previous Clipboard Insight history item."),
		gesture="kb:NVDA+alt+upArrow",
	)
	def script_previousClipboardInsightHistory(self, gesture):
		try:
			ui.message(self._history.previous().summary)
		except IndexError:
			ui.message(_("Clipboard Insight history is empty"))

	@scriptHandler.script(
		description=_("Reports the next Clipboard Insight history item."),
		gesture="kb:NVDA+alt+downArrow",
	)
	def script_nextClipboardInsightHistory(self, gesture):
		try:
			ui.message(self._history.next().summary)
		except IndexError:
			ui.message(_("Clipboard Insight history is empty"))
