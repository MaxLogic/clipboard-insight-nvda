from __future__ import annotations

from .metrics import measure_text


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
	if repeat_count == 1:
		return f"SPELL:{text}"
	if repeat_count > 1:
		return f"CHAR_DESC:{text}"
	return f"{text}. {_metrics_text(text)}"
