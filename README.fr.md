# TransLaTeX

[![pipeline status](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/pipeline.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/commits/main)
[![coverage report](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/coverage.svg)](https://cassandre.pages.math.unistra.fr/translatex/coverage)

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![fr](https://img.shields.io/badge/lang-fr-yellow.svg)](README.fr.md)

Vous trouverez ici le projet TransLaTeX qui a comme but de traduire des fichiers source LaTeX (`.tex`) d'une langue à
une autre à l'aide des traducteurs automatiques.

Voir la [documentation](https://cassandre.pages.math.unistra.fr/translatex) pour plus de détails.

## Dépôt Git

Le dépôt git de [ce projet](https://gitlab.math.unistra.fr/cassandre/translatex) suit une structure claire et déterminée
proposée par Vincent Driessen à son
poste "[A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)".

Du coup ne soyez pas surpris par le fait que `branch main` n'a presque pas de commit. Tout le développement se passe sur
le `branch develop`. Avant chaque version, tout est préparé et assuré fonctionnel pour être inauguré au `branch main`
qui n'a que des versions stables et complètes.

### Légende emoji

La signification des emojis utilisé dans les descriptions des commits git.

| Emoji       | Signification                                                         |
|:------------|:----------------------------------------------------------------------|
| ✨ NEW       | Nouveau fichier ou fonctionnalité                                     |
| 🔧 UPDATE   | Mise à jour d'une partie de programme                                 |
| 🔨 CONFIG   | Manipulation des fichiers de configuration comme makefile ou doxyfile |
| ♻️ REFACTOR | Réécriture d'une partie du programme                                  |
| 🐛 BUGFIX   | Une correction de bogue                                               |
| 🔥 DELETION | Suppression d'un fichier ou d'une fonctionnalité                      |
| 📝 DOC      | Manipulation de la documentation                                      |
| 🎉 EPOCH    | Le début du projet                                                    |
| 🚀 RELEASE  | Une nouvelle version du programme                                     |
