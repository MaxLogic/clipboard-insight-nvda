# Changelog

## Unreleased

### Added
- Initial Clipboard Insight add-on scaffold.
- Clipboard text reporting with character, word, line, and bundled `tiktoken` `o200k_base` token counts.
- Long clipboard text now reports counts first and reads the full text on repeated `NVDA+C`.
- File clipboard reporting for copied files, including first paths and remaining count.

### Fixed
- Load bundled helper libraries from the add-on private `lib` directory so NVDA can import the global plugin on startup.

### Removed
- In-memory clipboard history navigation and its default gestures.
