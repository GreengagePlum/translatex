# TransLaTeX

[![pipeline status](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/pipeline.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/commits/main)
[![coverage report](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/coverage.svg)](https://cassandre.pages.math.unistra.fr/translatex/coverage)

```{toctree}
:hidden:

modules/index
Git Repository <https://gitlab.math.unistra.fr/cassandre/translatex>

```

## Description

```{eval-rst}
.. automodule:: translatex
    :noindex:

```

The following is an overview on the inner processing stages of TransLaTeX.

```{eval-rst}
.. graphviz::
    :name: Processing Pipeline
    :caption: TransLaTeX data flow
    :alt: How TransLaTeX processes a given file
    :align: center

    digraph sphinx_doc {
        rankdir=LR; // Set the direction of the graph (left to right)
        node [shape=box]; // Set the shape of the nodes

        subgraph {
            label=""; // Set an empty label for the outer subgraph

            Input_Output [shape=oval]; // Set the shape of the "input" node to oval
            Cloud [shape=oval]; // Set the shape of the "Cloud" node to oval

            subgraph {
                label=""; // Set an empty label for the inner subgraph

                Preprocessor; // Add the "Preprocessor" node to the inner subgraph
                Marker; // Add the "Marker" node to the inner subgraph
                Tokenizer; // Add the "Tokenizer" node to the inner subgraph
                Translator; // Add the "Translator" node to the inner subgraph
            }
        }

        Input_Output -> Preprocessor [contraint=false]; // Arrow from input to Marker
        Preprocessor -> Marker [tailport=n, headport=n, contraint=false]; // Arrow from Marker to Tokenizer
        Marker -> Tokenizer [tailport=n, headport=n, contraint=false]; // Arrow from Marker to Tokenizer
        Tokenizer -> Translator [tailport=n, headport=n, contraint=false]; // Arrow from Tokenizer to Translator
        Translator -> Cloud [contraint=false]; // Arrow from Translator to Cloud

        Cloud -> Translator [contraint=false]; // Arrow from Cloud to Translator
        Translator -> Tokenizer [tailport=s, headport=s, contraint=false]; // Arrow from Translator to Tokenizer
        Tokenizer -> Marker [tailport=s, headport=s, contraint=false]; // Arrow from Tokenizer to Marker
        Marker -> Preprocessor [tailport=s, headport=s, contraint=false]; // Arrow from Tokenizer to Marker
        Preprocessor -> Input_Output [contraint=false]; // Arrow from Marker to input
    }

```

## Features

- Automatic translation for LaTeX
- Use a popular translation API of your choice
- Translate to and from a number of languages according to the translator you picked
- Replace all LaTeX constructs with tokens to be able to restore them later and still have a correct LaTeX file after
- Math environments and equations are kept intact while translating any text inside
- User customizable marker and token formats
- Provided syntax in your source LaTeX file to manually handle certain parts at your will
- Straight forward design, easy to tinker with the program's source code to customize its behavior
- Easy to install and run with simple instructions and CLI
- Debug option to have a peek at inner workings after the operation
- The core program apart from the API call is idempotent and preserves the original text from a LaTeX standpoint after
  any manipulation
- Correct resulting LaTeX, which compiles and has working references

### Unsupported and unmanaged so far

- Supports only a subset of LaTeX, doesn't recognize all constructs.
- LaTeX escape inside literal blocks isn't handled and doesn't get recursed into. They get tokenized as a whole. For
  example: `\begin{lstlisting}[escapeinside={\%*}{*)}]` which lets you escape actual LaTeX tags and commands inside
  a literal `lstlisting` block.
- Document header is kept untouched. Nothing in the header (before `\begin{document}`) gets tokenized or translated.
  Which means document `\date`, `\newcommand` and most importantly `babel` language specifier doesn't get
  translated.
- Any commands and metadata that can be put before `\begin{document}` should be put before and thus in the header.
  Otherwise, they will get tokenized and translated. More concisely, given file must be correct and conform LaTeX.
- Text inside math environments are kept intact for translation only if they are located one level deep. For example
  (albeit not the best example), the `\textsf` command's contents won't be translated since it is more than one level
  deep in a math environment in the following code block.

```latex
\begin{document}
    Soit la matrice
    \begin{equation}
        A=\left[\begin{array}{ccc}
                    3  & 3  & 4   \\
                    6  & -2 & -12 \\
                    -2 & 3  & 9
                    \textsf{hello world}
        \end{array}\right].\label{eq:A}
    \end{equation}
\end{document}
```

- Text inside math environments are recognized thanks to a list of valid text commands inside the `data` module
  named `TEXT_COMMANDS`. If there are others that we've missed, add them to this list so that they also get recognized.
- This program is built for LaTeX only. Use LaTeX commands almost exclusively and not pure TeX.
- Here is a list of known unsupported commands and environments:
    - `picture`
    - `tikzpicture`
- For now, only single file documents are supported. No `\input`.
- Macros are unsupported.
- The final full stop at the end of block math environments gets put into tokens instead of being left out. These dots
  should be kept alongside the text to be translated for it to form a logical sentence giving more consistent results
  with an automatic translator.

## Python versions

CPython is the Python implementation used and below are the most used versions during development.

```
Python 3.10.11
```

## Installation

### Install python package

#### Using pip

*For use as an end user, the final product*

```bash
pip install git+https://gitlab.math.unistra.fr/cassandre/translatex.git
```

#### Using pip in a virtual environment

*For use as a developer, a dev environment*

From project root directory:

```bash
git clone git@gitlab.math.unistra.fr:cassandre/translatex.git
cd translatex
python3 -m virtualenv .venv  # create a virtual environment
source .venv/bin/activate  # activate the virtual environment
pip install -e .  # install the package in editable mode
```

Note: in editable mode (`-e` option), the package is installed in a way that it is still possible to edit the source
code and have the changes take effect immediately.

### Run the unitary tests

#### Install the development dependencies

```bash
pip install -e ".[test]"
```

#### Run the tests

Run the tests from the projet root directory using the `-s`:

```bash
pytest -sv
```

See [.gitlab-ci.yml](https://gitlab.math.unistra.fr/cassandre/translatex/blob/main/.gitlab-ci.yml) for more details.

### Build the documentation

#### Install the documentation dependencies

```bash
pip install -e ".[doc]"
```

You also need [`graphviz`](https://graphviz.org/) for diagram generation. Install it according to its
official instructions and your system.

#### Build and serve the documentation locally

```bash
sphinx-autobuild docs/source/ docs/_build/html --watch src/
```

Go to <http://localhost:8000> and see the changes in `docs/source/` and `src/` directories take effect immediately.

## Usage

TransLaTeX reads from `stdin` and writes to `stdout` by default, but you can also pass in positional arguments
specifying the paths to the input and output files. It also writes warnings about missing or altered indicators
(generally due to the automatic translation) and extra information (when verbose) to `stderr`. Don't forget to redirect
these via `2> /dev/null` or equivalent if you only want the LaTeX output.

To be continued...

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
