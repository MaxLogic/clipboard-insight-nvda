# Clipboard Insight Tasks

Summary: 1 open, 0 in progress, 0 blocked, 5 done
Next task ID: T-007

## In Progress

## Next - Today

### T-006 [DOC] Finish docs and release metadata
Outcome:
- README and add-on user doc name every default gesture.
- Docs state token counts use `tiktoken` with `o200k_base` and fallback estimates only on tokenizer failure.
- Docs state clipboard contents are not logged and history is not persisted in v1.
- Package builds cleanly.
Proof:
- Run: `python -m unittest tests.test_scaffold`
  Expect: all pass
- Run: `python build.py`
  Expect: exit=0, stdout contains ".nvda-addon"
Touches: README.md, addon/doc/en/readme.md, CHANGELOG.md, addon/manifest.ini
Deps: T-005
Verify: unit-test, cli-proof
Notes: Plan slice 6.

## Next - This Week

## Next - Later

## Blocked

## Done

### T-005 [HISTORY] Add clipboard history navigation
Outcome:
- History deduplicates consecutive identical clipboard entries.
- Previous and next history commands are exposed with configurable default gestures.
- History stays in memory only.
Proof:
- Run: `python -m unittest tests.test_history tests.test_reporting`
  Expect: all pass
Touches: addon/globalPlugins/clipboardInsight.py, addon/globalPlugins/clipboardInsightLib/, tests/
Deps: T-004
Verify: unit-test
Notes: Plan slice 5. Completed with in-memory history and `NVDA+alt+upArrow` / `NVDA+alt+downArrow` defaults.

### T-004 [FILES] Report file clipboard content
Outcome:
- File clipboard summaries report one copied file with path and kind.
- Multiple copied files report the first three paths and remaining count.
- File summary code is isolated from Windows clipboard API calls so it can be unit-tested.
Proof:
- Run: `python -m unittest tests.test_files`
  Expect: all pass
Touches: addon/globalPlugins/clipboardInsightLib/, tests/test_files.py
Deps: T-002
Verify: unit-test
Notes: Plan slice 4. Completed with pointer-safe `CF_HDROP` wrapper signatures.

### T-003 [TEXT] Add long text repeat behavior
Outcome:
- First press on text over 1024 characters reports metrics without reading full text.
- Second press on long text reads full text and metrics.
- Short text repeat behavior preserves spell and character-description script branches.
Proof:
- Run: `python -m unittest tests.test_reporting`
  Expect: all pass
Touches: addon/globalPlugins/clipboardInsight.py, addon/globalPlugins/clipboardInsightLib/, tests/test_reporting.py
Deps: T-002
Verify: unit-test
Notes: Plan slice 3. Completed with README/add-on help documentation.

### T-002 [TEXT] Add clipboard text metrics
Outcome:
- Text metrics include characters, words, lines, and `tiktoken` token count using `o200k_base`.
- Fallback token counting is used only when `tiktoken` cannot load and labels tokens as estimated.
- Short text report content includes text plus metrics.
- Empty clipboard report says there is no text or file content.
Proof:
- Run: `python -m unittest tests.test_metrics tests.test_reporting`
  Expect: all pass
Touches: addon/globalPlugins/clipboardInsight.py, addon/globalPlugins/clipboardInsightLib/, tests/
Deps: T-001
Verify: unit-test
Notes: Plan slice 2. Completed with bundled offline `o200k_base` data, special-token literal handling, and fallback-estimated proof.

### T-001 [SCAFFOLD] Scaffold add-on repository
Outcome:
- Add-on manifest, README, build script, user doc stub, and global plugin module exist.
- `python build.py` creates a `.nvda-addon` package in `dist`.
- The global plugin module can be imported in tests with NVDA-only modules stubbed.
Proof:
- Run: `python -m unittest tests.test_scaffold`
  Expect: all pass
- Run: `python build.py`
  Expect: exit=0, stdout contains ".nvda-addon"
Touches: addon/manifest.ini, addon/globalPlugins/clipboardInsight.py, addon/doc/en/readme.md, README.md, CHANGELOG.md, build.py, tests/test_scaffold.py
Verify: unit-test, cli-proof
Notes: Plan slice 1. Completed with RED/GREEN proof; package created at `dist\maxlogicClipboardInsight-0.1.0.nvda-addon`.
