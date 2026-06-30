from __future__ import annotations

import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ADDON = ROOT / "addon"
DIST = ROOT / "dist"


def _manifest_value(key: str) -> str:
	match = re.search(rf"^{re.escape(key)}\s*=\s*(.+)$", (ADDON / "manifest.ini").read_text(encoding="utf-8"), re.M)
	if not match:
		raise ValueError(f"Missing manifest key: {key}")
	return match.group(1).strip().strip('"')


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
			if path.is_file() and "__pycache__" not in path.parts:
				archive.write(path, path.relative_to(ADDON).as_posix())
	temp_package.replace(package)
	print(package)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
