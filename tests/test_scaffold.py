import importlib.util
import subprocess
import sys
import types
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScaffoldTests(unittest.TestCase):
	def test_manifest_metadata(self):
		manifest_path = ROOT / "addon" / "manifest.ini"
		self.assertTrue(manifest_path.exists())
		manifest = manifest_path.read_text(encoding="utf-8")
		self.assertIn("name = maxlogicClipboardInsight", manifest)
		self.assertIn('summary = "Clipboard Insight"', manifest)

	def test_expected_files_exist(self):
		for relative in (
			"README.md",
			"CHANGELOG.md",
			"build.py",
			"addon/doc/en/readme.md",
			"addon/globalPlugins/clipboardInsight.py",
		):
			self.assertTrue((ROOT / relative).exists(), relative)

	def test_docs_include_long_text_behavior(self):
		for relative in ("README.md", "addon/doc/en/readme.md"):
			text = (ROOT / relative).read_text(encoding="utf-8")
			self.assertIn("Press `NVDA+C` twice to read the full text", text)
			self.assertIn("NVDA+Alt+UpArrow", text)
			self.assertIn("NVDA+Alt+DownArrow", text)

	def test_build_creates_addon_package(self):
		result = subprocess.run(
			[sys.executable, "build.py"],
			cwd=ROOT,
			text=True,
			capture_output=True,
		)
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIn(".nvda-addon", result.stdout)
		self.assertTrue(any((ROOT / "dist").glob("maxlogicClipboardInsight-*.nvda-addon")))

	def test_package_contains_addon_files(self):
		subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True, capture_output=True)
		package = next((ROOT / "dist").glob("maxlogicClipboardInsight-*.nvda-addon"))
		with zipfile.ZipFile(package) as archive:
			names = set(archive.namelist())
		self.assertIn("manifest.ini", names)
		self.assertIn("globalPlugins/clipboardInsight.py", names)
		self.assertIn("globalPlugins/tiktoken/_tiktoken.cp313-win_amd64.pyd", names)
		self.assertIn("globalPlugins/tiktoken/LICENSE", names)
		self.assertIn("globalPlugins/tiktoken_ext/data/o200k_base.tiktoken", names)
		self.assertIn("globalPlugins/tiktoken_ext/openai_public.py", names)
		self.assertIn("doc/en/readme.md", names)

	def test_global_plugin_imports_with_nvda_stubs(self):
		addon_handler = types.SimpleNamespace(initTranslation=lambda: None)
		api = types.SimpleNamespace(getClipData=lambda: "")
		ctypes_stub = types.ModuleType("ctypes")
		ctypes_stub.windll = types.SimpleNamespace()
		ctypes_stub.create_unicode_buffer = lambda size: [""] * size
		wintypes_stub = types.ModuleType("wintypes")
		ctypes_stub.wintypes = wintypes_stub
		global_plugin_handler = types.ModuleType("globalPluginHandler")
		global_plugin_handler.GlobalPlugin = type("GlobalPlugin", (), {})
		script_handler = types.SimpleNamespace(
			getLastScriptRepeatCount=lambda: 0,
			script=lambda **kwargs: lambda func: func,
		)
		speech = types.SimpleNamespace(speakSpelling=lambda *args, **kwargs: None)
		ui = types.SimpleNamespace(message=lambda text: None)
		original = {
			name: sys.modules.get(name)
			for name in ("addonHandler", "api", "ctypes", "ctypes.wintypes", "globalPluginHandler", "scriptHandler", "speech", "ui")
		}
		sys.modules["addonHandler"] = addon_handler
		sys.modules["api"] = api
		sys.modules["ctypes"] = ctypes_stub
		sys.modules["ctypes.wintypes"] = wintypes_stub
		sys.modules["globalPluginHandler"] = global_plugin_handler
		sys.modules["scriptHandler"] = script_handler
		sys.modules["speech"] = speech
		sys.modules["ui"] = ui
		try:
			path = ROOT / "addon" / "globalPlugins" / "clipboardInsight.py"
			spec = importlib.util.spec_from_file_location("clipboardInsightTest", path)
			module = importlib.util.module_from_spec(spec)
			module.__dict__["_"] = lambda text: text
			spec.loader.exec_module(module)
			self.assertTrue(hasattr(module, "GlobalPlugin"))
			source = path.read_text(encoding="utf-8")
			self.assertIn("kb:NVDA+alt+upArrow", source)
			self.assertIn("kb:NVDA+alt+downArrow", source)
		finally:
			for name, value in original.items():
				if value is None:
					sys.modules.pop(name, None)
				else:
					sys.modules[name] = value


if __name__ == "__main__":
	unittest.main()
