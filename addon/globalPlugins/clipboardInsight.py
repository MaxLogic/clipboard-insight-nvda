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
from clipboardInsightLib.windows_clipboard import get_clipboard_files


addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Clipboard Insight")

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
				ui.message(message)
				return
		repeat_count = scriptHandler.getLastScriptRepeatCount()
		if text and not text.isspace() and repeat_count and len(text) < LONG_TEXT_THRESHOLD:
			speech.speakSpelling(text, useCharacterDescriptions=repeat_count > 1)
			return
		message = report_text(text, repeat_count)
		ui.message(message)
