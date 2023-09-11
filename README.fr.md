# TransLaTeX

[![état du pipeline](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/pipeline.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/commits/main)
[![rapport de couverture](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/coverage.svg)](https://cassandre.pages.math.unistra.fr/translatex/coverage)
[![dernière version](https://gitlab.math.unistra.fr/cassandre/translatex/-/badges/release.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/releases/permalink/latest)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![fr](https://img.shields.io/badge/lang-fr-yellow.svg)](README.fr.md)

Vous trouverez ici le projet TransLaTeX qui a comme but de traduire des fichiers source LaTeX (`.tex`) d'une langue à
une autre à l'aide des traducteurs automatiques.

Voir la [documentation](https://cassandre.pages.math.unistra.fr/translatex) pour plus de détails sur l'utilisation et l'installation ainsi que comment préparer un environment de développement pour commencer à contribuer.

## Dépôt Git

Le dépôt git de [ce projet](https://gitlab.math.unistra.fr/cassandre/translatex) suit une structure claire et déterminée
proposée par Vincent Driessen à son
poste "[A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)".

Du coup ne soyez pas surpris par le fait que `branch main` n'a presque pas de commit. Tout le développement se passe sur
le `branch develop`. Avant chaque version, tout est préparé et assuré fonctionnel pour être inauguré au `branch main`
qui n'a que des versions stables et complètes.

### Légende emoji

La signification des emojis utilisé dans les descriptions des commits git. À voir
aussi : [gitmoji](https://gitmoji.dev/).

| Emoji              | Signification                                                         |
|:-------------------|:----------------------------------------------------------------------|
| :sparkles: NEW     | Nouveau fichier ou fonctionnalité                                     |
| :wrench: UPDATE    | Mise à jour d'une partie de programme                                 |
| :hammer: CONFIG    | Manipulation des fichiers de configuration comme makefile ou doxyfile |
| :recycle: REFACTOR | Réécriture d'une partie du programme                                  |
| :bug: BUGFIX       | Une correction de bogue                                               |
| :fire: DELETION    | Suppression d'un fichier ou d'une fonctionnalité                      |
| :memo: DOC         | Manipulation de la documentation                                      |
| :tada: EPOCH       | Le début du projet                                                    |
| :rocket: RELEASE   | Une nouvelle version du programme                                     |
