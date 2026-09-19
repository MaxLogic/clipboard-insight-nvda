from __future__ import annotations

from .metrics import measure_text


LONG_TEXT_THRESHOLD = 1024


def _plural(count: int, singular: str, plural: str | None = None) -> str:
	return f"{count} {singular if count == 1 else (plural or singular + 's')}"


def _metrics_text(text: str) -> str:
	metrics = measure_text(text)
	token_label = "estimated tokens" if metrics.tokens_estimated else "tokens"
	return ", ".join(
		(
			_plural(metrics.characters, "character"),
			_plural(metrics.words, "word"),
			_plural(metrics.lines, "line"),
			f"{metrics.tokens} {token_label}",
		),
	)


def report_text(text: str, repeat_count: int) -> str:
	if not text or text.isspace():
		return "There is no text or file content on the clipboard"
	if len(text) >= LONG_TEXT_THRESHOLD:
		if repeat_count == 0:
			return f"The clipboard contains a large amount of text. {_metrics_text(text)}. Press NVDA+c twice to read it."
		return f"{text}. {_metrics_text(text)}"
	if repeat_count == 1:
		return f"SPELL:{text}"
	if repeat_count > 1:
		return f"CHAR_DESC:{text}"
	return f"{text}. {_metrics_text(text)}"


def split_for_reading(text: str, max_chars: int) -> list[str]:
	"""Split text into blocks of at most max_chars that join back into the text.

	Blocks end at a line break if one is in the second half of the block, else at a
	sentence end, else at a space. Text without any of those is cut at max_chars.
	"""
	blocks = []
	start = 0
	while len(text) - start > max_chars:
		window = text[start:start + max_chars]
		half = max_chars // 2
		cut = window.rfind("\n") + 1
		if cut <= half:
			cut = max(window.rfind(end) for end in (". ", "! ", "? ")) + 2
		if cut <= half:
			cut = window.rfind(" ") + 1
		if cut <= 0:
			cut = max_chars
		blocks.append(text[start:start + cut])
		start += cut
	if start < len(text):
		blocks.append(text[start:])
	return blocks
