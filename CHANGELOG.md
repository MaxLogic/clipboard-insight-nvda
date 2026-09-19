# Changelog

## 0.2.0

- Pressing NVDA+C twice on a long clipboard reads the text in blocks of about 2000 characters, as NVDA's say all does. NVDA stays responsive, and Control stops the reading at once. Before, NVDA prepared the whole text at once and could not be interrupted until it was done.
- NVDA no longer freezes while tokens are counted. The first NVDA+C used to freeze NVDA for about 1.3 s while the tokenizer loaded, and a 5 MB clipboard for about 2 s.
- Reading copied files no longer changes Windows API definitions that NVDA and other add-ons share.

## 0.1.1

- Update compatibility metadata for NVDA 2026.2 and the bundled Python 3.13 libraries.

## 0.1.0

### Added
- Initial Clipboard Insight add-on scaffold.
- Clipboard text reporting with character, word, line, and bundled `tiktoken` `o200k_base` token counts.
- Long clipboard text now reports counts first and reads the full text on repeated `NVDA+C`.
- File clipboard reporting for copied files, including first paths and remaining count.

### Fixed
- Load bundled helper libraries from the add-on private `lib` directory so NVDA can import the global plugin on startup.

### Removed
- In-memory clipboard history navigation and its default gestures.
