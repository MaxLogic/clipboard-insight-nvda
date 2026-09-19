# Clipboard Insight

Clipboard Insight is an NVDA add-on that improves clipboard reporting with text statistics and file summaries.

This repository is under active development.

## Use

- Press `NVDA+C` once to report clipboard text with character, word, line, and token counts.
- If the clipboard contains long text, the first press reports only the counts. Press `NVDA+C` twice to read the full text.
- If the clipboard contains short text, press `NVDA+C` twice to spell it, or three times to spell it with character descriptions.
- If you copied files, `NVDA+C` reports how many files are on the clipboard and names up to three of them.

NVDA stays responsive while Clipboard Insight counts tokens. The first report after NVDA starts, or the report for a very large clipboard, can take a second or two to be spoken. If you press `NVDA+C` again before an earlier report is ready, only the newest report is spoken.

Token counts use bundled `tiktoken` with the `o200k_base` encoding. If the tokenizer cannot load, Clipboard Insight falls back to estimated token counts and says they are estimated.

Clipboard contents are not logged or persisted.

## Build

Run:

```powershell
python build.py
```

The package is written to `dist`.
