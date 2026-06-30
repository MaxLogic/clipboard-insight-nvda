# Clipboard Insight

Clipboard Insight is an NVDA add-on that improves clipboard reporting with text statistics and file summaries.

This repository is under active development.

## Use

- Press `NVDA+C` once to report clipboard text with character, word, line, and token counts.
- If the clipboard contains long text, the first press reports only the counts. Press `NVDA+C` twice to read the full text.

Token counts use bundled `tiktoken` with the `o200k_base` encoding. If the tokenizer cannot load, Clipboard Insight falls back to estimated token counts and says they are estimated.

Clipboard contents are not logged or persisted.

## Build

Run:

```powershell
python build.py
```

The package is written to `dist`.
