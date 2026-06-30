# Clipboard Insight

Clipboard Insight is an NVDA add-on that improves clipboard reporting with text statistics, file summaries, and clipboard history navigation.

This repository is under active development.

## Use

- Press `NVDA+C` once to report clipboard text with character, word, line, and token counts.
- If the clipboard contains long text, the first press reports only the counts. Press `NVDA+C` twice to read the full text.
- Press `NVDA+Alt+UpArrow` or `NVDA+Alt+DownArrow` to move through Clipboard Insight history captured during clipboard reports.

## Build

Run:

```powershell
python build.py
```

The package is written to `dist`.
