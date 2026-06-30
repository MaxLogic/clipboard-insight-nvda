import addonHandler
import api
import globalPluginHandler
import scriptHandler
import speech
import ui

from clipboardInsightLib.reporting import report_text


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
		repeat_count = scriptHandler.getLastScriptRepeatCount()
		if text and not text.isspace() and repeat_count:
			speech.speakSpelling(text, useCharacterDescriptions=repeat_count > 1)
			return
		ui.message(report_text(text, repeat_count))
