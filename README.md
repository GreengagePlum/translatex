# TransLaTeX

[![pipeline status](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/pipeline.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/commits/main)
[![coverage report](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/coverage.svg)](https://cassandre.pages.math.unistra.fr/translatex/coverage)
[![latest release](https://gitlab.math.unistra.fr/cassandre/translatex/-/badges/release.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/releases/permalink/latest)

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![fr](https://img.shields.io/badge/lang-fr-yellow.svg)](README.fr.md)

You'll find here the TransLaTeX project which aims to translate LaTeX source files (`.tex`) from one human language to
another using automatic translators.

See the [documentation](https://cassandre.pages.math.unistra.fr/translatex) for details.

## Git repository

The git repository of [this project](https://gitlab.math.unistra.fr/cassandre/translatex) follows a clear and determined
structure put forth by Vincent Driessen in his
post "[A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)".

So don't be surprised by the fact that the `main branch` has few commits. All the development is happening on
the `develop branch`. Before each version, everything is prepared and guaranteed functional to be merged
into `main branch` which only has stable and complete versions.

### Emoji legend

These are the meanings of the emojis used in the git commit messages. See [gitmoji](https://gitmoji.dev/) also.

| Emoji              | Meaning                                            |
|:-------------------|:---------------------------------------------------|
| :sparkles: NEW     | New file or feature                                |
| :wrench: UPDATE    | Update of a part of the program                    |
| :hammer: CONFIG    | Changes in config files like makefile and doxyfile |
| :recycle: REFACTOR | Rewrite of a part of the program                   |
| :bug: BUGFIX       | A bug fix                                          |
| :fire: DELETION    | Removal of a file or a feature                     |
| :memo: DOC         | Changes in the documentation                       |
| :tada: EPOCH       | The beginning of the project                       |
| :rocket: RELEASE   | A new version of the program                       |
