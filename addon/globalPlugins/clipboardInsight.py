from pathlib import Path
import sys
import threading

import addonHandler
import api
import globalPluginHandler
import queueHandler
import scriptHandler
import speech
import ui


_LIB = Path(__file__).resolve().parents[1] / "lib"
if str(_LIB) not in sys.path:
	sys.path.insert(0, str(_LIB))

from clipboardInsightLib.reporting import LONG_TEXT_THRESHOLD, report_text, split_for_reading
from clipboardInsightLib.files import summarize_files
from clipboardInsightLib.windows_clipboard import get_clipboard_files


addonHandler.initTranslation()

# Longer reports are read one block at a time, like NVDA's say-all: NVDA prepares
# each block quickly, and Control stops the reading at once.
READ_BLOCK_CHARS = 2000


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Clipboard Insight")
	# Counts presses, so a slow report for an earlier press is never spoken after a newer one.
	_latestRequest = 0

	@scriptHandler.script(
		description=_("Reports clipboard text with characters, words, and token count."),
		gesture="kb:NVDA+c",
	)
	def script_reportClipboardText(self, gesture):
		self._latestRequest += 1
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
		self._reportInBackground(text, repeat_count)

	def _reportInBackground(self, text, repeatCount):
		# Loading the tokenizer takes over a second, and a large clipboard takes seconds to count.
		# Doing that on NVDA's main thread would freeze NVDA.
		request = self._latestRequest

		def work():
			message = report_text(text, repeatCount)
			queueHandler.queueFunction(queueHandler.eventQueue, self._speakIfLatest, request, message)

		threading.Thread(target=work, name="ClipboardInsightReport", daemon=True).start()

	def _speakIfLatest(self, request, message):
		if request != self._latestRequest:
			return
		if len(message) <= READ_BLOCK_CHARS:
			ui.message(message)
			return
		self._readBlocks(request, split_for_reading(message, READ_BLOCK_CHARS), 0)

	def _readBlocks(self, request, blocks, index):
		# NVDA drops the callbacks of cancelled speech, so Control ends the chain. A newer press ends it too.
		if request != self._latestRequest:
			return
		from speech.commands import CallbackCommand
		sequence = [blocks[index]]
		if index + 1 < len(blocks):
			# Runs when speech starts this block, so the next one is always queued behind it.
			sequence.insert(0, CallbackCommand(
				lambda: self._readBlocks(request, blocks, index + 1), name="clipboardInsight.nextBlock"))
		speech.speak(sequence)
