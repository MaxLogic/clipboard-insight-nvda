from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path

import markdown


ROOT = Path(__file__).resolve().parent
ADDON = ROOT / "addon"
DIST = ROOT / "dist"


def _manifest_value(key: str) -> str:
	match = re.search(rf"^{re.escape(key)}\s*=\s*(.+)$", (ADDON / "manifest.ini").read_text(encoding="utf-8"), re.M)
	if not match:
		raise ValueError(f"Missing manifest key: {key}")
	return match.group(1).strip().strip('"')


def _doc_html(source: Path) -> str:
	"""NVDA opens docFileName with the default app, so ship the user guide as HTML."""
	text = source.read_text(encoding="utf-8")
	title_match = re.search(r"^# (.+)$", text, re.M)
	title = html.escape(title_match.group(1) if title_match else "Clipboard Insight")
	body = markdown.markdown(text)
	lang = source.parent.name.replace("_", "-")
	return "\n".join((
		"<!DOCTYPE html>",
		f'<html lang="{lang}">',
		'<head><meta charset="utf-8">',
		f"<title>{title}</title></head>",
		"<body>",
		body,
		"</body>",
		"</html>",
		"",
	))


def main() -> int:
	name = _manifest_value("name")
	version = _manifest_value("version")
	DIST.mkdir(exist_ok=True)
	package = DIST / f"{name}-{version}.nvda-addon"
	temp_package = package.with_suffix(package.suffix + ".tmp")
	if temp_package.exists():
		temp_package.unlink()
	with zipfile.ZipFile(temp_package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
		for path in ADDON.rglob("*"):
			if not path.is_file() or "__pycache__" in path.parts:
				continue
			relative = path.relative_to(ADDON)
			if relative.parts[0] == "doc" and path.name == "readme.md":
				archive.writestr(relative.with_name("readme.html").as_posix(), _doc_html(path))
			else:
				archive.write(path, relative.as_posix())
	temp_package.replace(package)
	print(package)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
