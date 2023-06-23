# TODO

## Bugs & Fixes

- [ ] Fix math environment preserving of any text that is located deep caused by earlier optimization
- [ ] Add guardrails to keep from operating on empty strings in all stages
- [ ] Fix tokenization issue (regex) caused by nested curly braces

## Features

- [ ] Add verifications on token and marker presence
- [ ] Improve Marker
    - [x] Add manual substitution/ignore syntax
    - [ ] Manage displaymath ending with a dot
- [ ] Finish Translator
    - [ ] Additional APIs
    - [ ] Doc and test
- [ ] Finish CLI
    - [x] Add options to stop at certain stages (marking, tokenization...)
    - [x] Debug/verbose mode (?)
    - [ ] Doc and test
- [ ] Create a web interface
- [ ] Let the user enter regex or similar extra logic
- [ ] Make `__str__()` methods more useful
- [ ] Optimizations
    - [ ] Generate as few tokens as possible (possibly multiple runs regrouping adjacent tokens)
    - [ ] Don't send any split sequences that solely contain tokens.

## Configuration

- [ ] Implement docker
- [ ] Configure CI/CD further

## Miscellaneous

- [ ] Add `CONTRIBUTING.md`
- [ ] Finish Sphinx main page
    - [ ] Document interface and features for the end user
- [ ] Fill `CHANGELOG.md`

## Done

- [x] Add use case/functioning schema to doc (UML)
- [x] Digitize the unmanaged list of features
- [x] Finish Tokenizer
    - [x] Implement token store for each regex substitution method
    - [x] Finish detokenizer
        - [x] Add complex regex reconstruction for tokens followed by curly braces
        - [x] Lastly, add simple search and replace with all the rest
- [x] Fix "\item[]" command losing square bracket contents during tokenization
