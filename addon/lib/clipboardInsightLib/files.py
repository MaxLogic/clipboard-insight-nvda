from __future__ import annotations

from pathlib import PureWindowsPath


KIND_BY_EXTENSION = {
	".doc": "Word document",
	".docx": "Word document",
	".pdf": "PDF file",
	".png": "PNG image",
	".txt": "text file",
	".zip": "ZIP archive",
}


def _kind(path: str) -> str:
	return KIND_BY_EXTENSION.get(PureWindowsPath(path).suffix.lower(), "file")


def summarize_files(paths: list[str]) -> str:
	if not paths:
		return "There is no text or file content on the clipboard"
	if len(paths) == 1:
		path = paths[0]
		return f"1 file on the clipboard: {path}, {_kind(path)}"
	head = ", ".join(paths[:3])
	remaining = len(paths) - 3
	suffix = f", and {remaining} more" if remaining > 0 else ""
	return f"{len(paths)} files on the clipboard: {head}{suffix}"
