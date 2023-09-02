# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2023-09-02

### Added

- 2 new example LaTeX files
- GitLab footer icon in docs
- CLI synopsis page to docs
- `livehtml` target to Sphinx Makefile that launches `sphinx-autobuild`
- New CI/CD job to test doc generation
- Any custom translation service can be added to the CLI
- tranlatex can be run as a module
- DeepL translation service
- Add an `ApiKeyError` exception
- Create a release from a tag in CI/CD

### Changed

- Increase amount of information logged in case of unexpected API response
- Select translation service by its name making it more explicit
- Make tests that use paid API optional with a custom pytest CLI option (`--runapi`)
- Add sub menu for modules in the doc sidebar
- Add link to project GitLab repo in the doc sidebar
- Unicode emojis to plain text emojis in READMEs
- Unnecessary read-write file accesses to write-only in main
- Logging behaviour is restored to initial intended functionality respecting CLI option distinction (`-v` and `-d`)
- Fix Sphinx version to solve a Furo extension bug

### Removed

- Erroneous example LaTeX file
- `IRMA - M2M100` translation service (now a custom service)

### Fixed

- Missing hyperlink in CHANGELOG.md
- Missing debug info in log about Tokenizer
- Close infile and outfile in main
- Update out of sync docstrings
- Missing new line at EOF of translated files due to translation
- Add missing dependency of example LaTeX file
- Commands in installation instructions
- Tokenization of multi-argument LaTeX commands (with multiple `{}`)
- Idempotency issue introducing whitespace between arguments of LaTeX commands where there were none
- Wrong detection of math environments on encounter of backslash escaped characters (`\$`, `\\[`...)

## [0.2.0] - 2023-07-19

### Added

- Handle multiple translation services
- Improve test coverage
- Handle latex code without any document environment
- Use logging module
- Expose an interface to translatex_web

### Fixed

- Splitting in sentences now works using nltk
- Use a default token format compatible with Google Translate

## [0.1.0] - 2023-06-29

### Added

- Checks on missing or altered indicators on all stages
- A working, almost complete CLI
- New methods to dump indicator, marker and token store contents (for debugging mostly)
- New `Translator` class to cut up the string and do the API calls for the translation (incomplete)

### Changed

- Now all backslash escaped single characters get tokenized at the very end (eg. `\, \: \{`...)

### Removed

- `LATEX_SPACERS` list in `data` module that used to indicate a bunch of backslash escaped characters to tokenize

### Fixed

- A lot of regexes have been fixed and improved
- Correct some example files

## [0.0.3] - 2023-06-21

### Added

- Graphviz graph to doc to illustrate program data flow
- Syntax for manual substitution by the end user
- Unsupported features are now listed in the doc
- New syntax in LaTeX source file to manually replace lines for the end user
- New `Preprocessor` class to handle manual substitution syntax

### Changed

- Pinned CI/CD Python Docker image to version `3.10.11`

### Removed

- Disabled missing or altered marker error

## [0.0.2] - 2023-06-16

### Added

- New `Tokenizer` class to replace constructs with tokens before translation
- A demo semi-automatic CLI for proof of concept
- Lots of documentation and tests

### Changed

- Python version from `3.8.9` to `3.10.11`

### Removed

- `translatex.py` script due to name collision with package and import problems

## [0.0.1] - 2023-06-02

### Added

- New `Marker` class to traverse the AST of LaTeX files
- French `README.md`
- To-do list `TODO.md`

### Changed

- Updated readme files' structure and content

[unreleased]: https://gitlab.math.unistra.fr/cassandre/translatex/compare/v0.3.0...HEAD

[0.3.0]: https://gitlab.math.unistra.fr/cassandre/translatex/compare/v0.2.0...v0.3.0

[0.2.0]: https://gitlab.math.unistra.fr/cassandre/translatex/compare/v0.1.0...v0.2.0

[0.1.0]: https://gitlab.math.unistra.fr/cassandre/translatex/compare/v0.0.3...v0.1.0

[0.0.3]: https://gitlab.math.unistra.fr/cassandre/translatex/compare/v0.0.2...v0.0.3

[0.0.2]: https://gitlab.math.unistra.fr/cassandre/translatex/compare/v0.0.1...v0.0.2

[0.0.1]: https://gitlab.math.unistra.fr/cassandre/translatex/releases/tag/v0.0.1
