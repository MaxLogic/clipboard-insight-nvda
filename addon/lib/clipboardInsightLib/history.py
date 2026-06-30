from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryItem:
	kind: str
	summary: str
	key: str


class ClipboardHistory:
	def __init__(self, limit: int = 20):
		self.limit = limit
		self.items: list[HistoryItem] = []
		self.index = 0

	def add(self, kind: str, summary: str, key: str) -> None:
		item = HistoryItem(kind, summary, key)
		if self.items and self.items[-1].kind == kind and self.items[-1].key == key:
			self.index = len(self.items) - 1
			return
		self.items.append(item)
		self.items = self.items[-self.limit :]
		self.index = len(self.items) - 1

	def previous(self) -> HistoryItem:
		if not self.items:
			raise IndexError("clipboard history is empty")
		self.index = max(0, self.index - 1)
		return self.items[self.index]

	def next(self) -> HistoryItem:
		if not self.items:
			raise IndexError("clipboard history is empty")
		self.index = min(len(self.items) - 1, self.index + 1)
		return self.items[self.index]
