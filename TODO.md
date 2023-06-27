# TODO

## Bugs & Fixes

- [ ] Fix math environment preserving of any text that is located deep caused by earlier optimization

## Features

- [ ] Improve verifications on token and marker presence (highlight the supposed location of the missing indicator)
- [ ] Improve `Marker`
    - [x] Add manual substitution/ignore syntax
    - [ ] Manage `displaymath` ending with a dot
- [ ] Finish `Translator`
    - [ ] Additional APIs
    - [ ] Doc and test
- [ ] Create a web interface
- [ ] Let the user enter regex or similar extra logic
- [ ] Make `__str__()` methods more useful
- [ ] Optimizations
    - [ ] Generate as few tokens as possible (possibly multiple runs regrouping adjacent tokens)
    - [ ] Don't send any split sequences that solely contain tokens.
- [ ] Add option to "flatten" multi-file LaTeX projects into a single file
- [ ] Create a LaTeX object to store the string to operate on (dissected into preamble, document, etc.)

## Configuration

- [ ] Implement docker
- [ ] Configure CI/CD further

## Miscellaneous

- [ ] Add `CONTRIBUTING.md`
- [ ] Finish Sphinx main page
    - [ ] Document interface and features for the end user
- [ ] Fill `CHANGELOG.md`
- [ ] Add `argcomplete` for shell option completions

## Done

- [x] Add verifications on token and marker presence
- [x] Finish CLI
    - [x] Add options to stop at certain stages (marking, tokenization...)
    - [x] Debug/verbose mode (?)
    - [x] Doc
- [x] Add guardrails to keep from operating on empty strings in all stages
- [x] Fix tokenization issue (regex) caused by nested curly braces
- [x] Add use case/functioning schema to doc (UML)
- [x] Digitize the unmanaged list of features
- [x] Finish Tokenizer
    - [x] Implement token store for each regex substitution method
    - [x] Finish detokenizer
        - [x] Add complex regex reconstruction for tokens followed by curly braces
        - [x] Lastly, add simple search and replace with all the rest
- [x] Fix `\item[]` command losing square bracket contents during tokenization
