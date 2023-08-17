# Modules

Here you can find the documentation for the modules that compose TransLaTeX. This is the technical part of the
documentation intended to explain the inner workings of TransLaTeX for those that are interested or for developers.
The logic of the various processing layers each reside in their relatively named module. {mod}`~translatex.data` is a
place for global variables accessed by multiple layers at certain times and {mod}`~translatex.main` is the where it all
comes together as a whole process pipeline as well as the CLI.

Feel free to [open an issue](https://gitlab.math.unistra.fr/cassandre/translatex/issues/new) if you want to discuss your
findings or [create a fork](https://gitlab.math.unistra.fr/cassandre/translatex/forks/new)
and [submit a merge request](https://gitlab.math.unistra.fr/cassandre/translatex/merge_requests/new) for any changes or
improvements you feel could benefit the project.

```{toctree}
:maxdepth: 2
:glob:

*
```
