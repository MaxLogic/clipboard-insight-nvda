from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class TextMetrics:
	characters: int
	words: int
	lines: int
	tokens: int
	tokens_estimated: bool = False


def _load_o200k_encoding():
	import tiktoken

	return tiktoken.get_encoding("o200k_base")


def _count_tokens(text: str) -> tuple[int, bool]:
	try:
		encoding = _load_o200k_encoding()
	except Exception:
		return max(1, round(len(text) / 4)), True
	return len(encoding.encode(text, disallowed_special=())), False


def measure_text(text: str) -> TextMetrics:
	tokens, estimated = _count_tokens(text)
	return TextMetrics(
		characters=len(text),
		words=len(re.findall(r"\S+", text)),
		lines=0 if not text else text.count("\n") + 1,
		tokens=tokens,
		tokens_estimated=estimated,
	)
