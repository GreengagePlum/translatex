# TODO

## Bugs & Fixes

- [ ]

## Features

- [ ] Add verifications on token and marker presence
- [ ] Improve Marker
    - [ ] Add manual substitution/ignore syntax
    - [ ] Manage displaymath ending with a dot
- [ ] Finish Translator
- [ ] Finish CLI
    - [ ] Add options to stop at certain stages (marking, tokenization...)
    - [ ] Debug/verbose mode (?)
- [ ] Create a web interface
- [ ] Let the user enter regex or similar extra logic

## Configuration

- [ ] Implement docker
- [ ] Configure CI/CD further

## Miscellaneous

- [ ] Add `CONTRIBUTING.md`
- [ ] Add use case/functioning schema to doc (UML)

## Done

- [x] Digitize unmanaged list of features
- [x] Finish Tokenizer
    - [x] Implement token store for each regex substitution method
    - [x] Finish detokenizer
        - [x] Add complex regex reconstruction for tokens followed by curly braces
        - [x] Lastly, add simple search and replace with all the rest
- [x] Fix "\item[]" command losing square bracket contents during tokenization
