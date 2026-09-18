from __future__ import annotations

import ctypes
from ctypes import wintypes


CF_HDROP = 15


def _configure_clipboard_api(user32, shell32) -> None:
	user32.OpenClipboard.argtypes = [wintypes.HWND]
	user32.OpenClipboard.restype = wintypes.BOOL
	user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
	user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
	user32.GetClipboardData.argtypes = [wintypes.UINT]
	user32.GetClipboardData.restype = wintypes.HANDLE
	user32.CloseClipboard.argtypes = []
	user32.CloseClipboard.restype = wintypes.BOOL
	shell32.DragQueryFileW.argtypes = [wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT]
	shell32.DragQueryFileW.restype = wintypes.UINT


_api = None


def _clipboard_api():
	# Own DLL handles: ctypes.windll is shared with NVDA and every add-on, and these prototypes would change theirs.
	global _api
	if _api is None:
		user32 = ctypes.WinDLL("user32")
		shell32 = ctypes.WinDLL("shell32")
		_configure_clipboard_api(user32, shell32)
		_api = user32, shell32
	return _api


def get_clipboard_files() -> list[str]:
	user32, shell32 = _clipboard_api()
	if not user32.OpenClipboard(None):
		return []
	try:
		if not user32.IsClipboardFormatAvailable(CF_HDROP):
			return []
		handle = user32.GetClipboardData(CF_HDROP)
		if not handle:
			return []
		count = shell32.DragQueryFileW(handle, 0xFFFFFFFF, None, 0)
		paths = []
		for index in range(count):
			length = shell32.DragQueryFileW(handle, index, None, 0)
			buffer = ctypes.create_unicode_buffer(length + 1)
			shell32.DragQueryFileW(handle, index, buffer, length + 1)
			paths.append(buffer.value)
		return paths
	finally:
		user32.CloseClipboard()
