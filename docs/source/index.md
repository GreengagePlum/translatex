# TransLaTeX

[![pipeline status](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/pipeline.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/commits/main)
[![coverage report](https://gitlab.math.unistra.fr/cassandre/translatex/badges/main/coverage.svg)](https://cassandre.pages.math.unistra.fr/translatex/coverage)
[![latest release](https://gitlab.math.unistra.fr/cassandre/translatex/-/badges/release.svg)](https://gitlab.math.unistra.fr/cassandre/translatex/-/releases/permalink/latest)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

```{toctree}
:hidden:

cli-synopsis
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

- Text inside math environments are recognized thanks to a list of valid text commands inside the
  {mod}`~translatex.data` module named {data}`~translatex.data.TEXT_COMMANDS`. If there are others that we've missed,
  add them to this list so that they also get recognized.
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
pip install -e ".[test,doc,dev]"  # install the package in editable mode with optional dependnecies
pre-commit install  # install git hooks
pre-commit run -a   # run git hooks once for the first time
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

Also add the `--runapi` option to run all the tests including the optional ones that require a Google Translate API key.

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
sphinx-autobuild docs/source/ docs/_build/html --watch src/ --ignore "**/docs/source/manually_generated_content/*"
```

Go to <http://localhost:8000> and see the changes in `docs/source/` and `src/` directories take effect immediately.

## Usage

### Basic use

```{note}
See the [](cli-synopsis.md) for an overview of the possible options for TransLaTeX on the command line.
```

TransLaTeX reads from `stdin` and writes to `stdout` by default, but you can also pass in positional arguments
specifying the paths to the input and output files. It also writes warnings about missing or altered indicators
(generally due to the automatic translation) and extra information when verbose or debug options are specified as
logs to `stderr`. Don't forget to redirect these via `2> /dev/null` or equivalent if you only want the LaTeX output.
This behaviour is useful if you want to integrate TransLaTeX into scripts, batch execute it, automate its execution
or simply use a pipe (`|`) syntax.

```{note}
You can find various small LaTeX files under the [`translatex/examples/`](https://gitlab.math.unistra.fr/cassandre/translatex/-/tree/main/examples) directory in the source code that serve as examples that you can use to experiment with the program.
```

For the most basic invocation of TransLaTeX, you need the source and destination language short names and an internet
connection. An example is as follows:

```bash
translatex -sl en -dl fr
```

This reads from `stdin` and outputs the resulting LaTeX file in French to `stdout` as there were no file names specified
for the output. The input LaTeX file is expected to be in English as per the passed option.

* `-sl` or `--src-lang` specifies the source language which is the language of your input file
* `-dl` or `--dest-lang` specifies the destination language which is the language you want for your translated result.

```{note}
The available languages depend on the chosen translation service and its supported languages.

To learn more about which translation service integrations are available and how you can add your own, see {mod}`~translatex.translator`.
```

If you're not scripting but instead using TransLaTeX yourself, you most likely have already existing LaTeX files to
translate.

For a more common use, you need a correct LaTeX file. An example is as follows:

```bash
translatex -sl en -dl fr input.tex output.tex
```

* `input.tex` is an existing LaTeX file, written in your previously specified source language, to be processed by
  TransLaTeX. This can be omitted by passing `-` instead, if you want to still read from `stdin` but output to a file.
* `output.tex` is the file to write the translated output to. If it doesn't exist, it is created. If it already
  exists, it is overwritten.

Lastly for this example, since we didn't explicitly specify a translation service to use, the default service of
`Google Translate (no key)` is used. This is a free, unlimited use service that produces lesser quality results. It
is intended for testing and educational purposes, and it violates Google's TOS. This is equivalent to explicitly
specifying
`--service "Google Translate (no key)"` as an option (read on for more info).

### Common options

Let's see another example where we use Google's official translation API and output to a file instead.

```bash
translatex -sl en -dl fr --service "Google Translate" input.tex output.tex
```

* `--service` option lets you choose one of the available translation services to use.

According to the translation service that you choose to use, you may want to change the token format generated by
TransLaTeX to one that works better. The default is `[{}-{}]` since this seems to work best with Google's translation.

For example, you can do the following to get better results if the default format tokens get corrupted after the
translation. Suppose `={}.{}=` format works better with `IRMA - M2M100`:

```bash
translatex -sl en -dl fr --service "IRMA - M2M100" -tf "={}.{}=" input.tex output.tex
```

This makes it so that TransLaTeX generates tokens in your custom specified format before sending out the tokenized
text for translation. The curly braces (`{}`) indicate where numbers will be put during the numbering of the tokens.
For example a token with the previous format could be like `=12.6=` or `[12-6]` with the default format. The tokens
use two numbers so their format string has to contain at least two distinct pairs of curly braces.

```{note}
See the [](#extra-options) section to find out details on how to visualize the tokens and the
generation of intermediary files to have a peek at the inner workings of TransLaTeX.
```

If you want to show logs and have more information on the execution of TransLaTeX, you can use the `-v` or `-vv`
flags for verbose output. These output logs of `INFO` level or higher to `stderr`. The former shows info on only
TransLaTeX and the latter on all, including the imported modules, making for a more detailed output.

```{note}
For even more details on the logging behaviour of TransLaTeX, see {func}`~translatex.main.main`.
```

#### Manual substitution syntax

It is possible to exclude certain parts of your LaTeX file from the automatic translation with some special
TransLaTeX preprocessor syntax (see {meth}`~translatex.preprocessor.Preprocessor.process`). This is useful if
TransLaTeX doesn't
recognize certain structures in your LaTeX file or the automatic translation produces a poor quality translation that
you want to provide by hand. The manual substitution block's syntax is as follows inside a LaTeX file:

```latex
%@{            -> Beginning indicator
\textbf{Welcome to France!}
%@--           -> Seperator indicator
\textit{Bienvenue en France !}
% $x < 3$
%@}            -> Ending indicator
```

The top section (before `%@--`) of the block is considered the original text and the bottom part is the replacement
text. Default behaviour is to remove these blocks before any further processing thus preventing them from being sent
to parsing and translation. After the translation, the bottom part of the block is put where the block once was thus
producing:

```latex
\textit{Bienvenue en France !}
$x < 3$
```

The commented out lines in the replacement section are uncommented before any replacement. Notice the second line is no
longer a comment.

In short,

* Use `%@{` and `%@}` to begin and end a block.
* Use `%@--` to separate the original lines and the lines that will replace those.
* Any commented out lines in the bottom part are uncommented before replacing.

You can write anything on the same lines as these indicators without causing issues just like in the given example.
This allows you to annotate your manual replacement blocks. One use could be to continue with the number of dashes
to improve visibility:

```latex
%@{ This is my very special block
\textbf{Welcome to France!}
%@-----------------------------------
\textit{Bienvenue en France !}
% $x < 3$
%@} For anyone wondering, this block is for TransLaTeX
```

This syntax is compatible with LaTeX as it uses the line comment character (`%`) and is invisible to it. Files that
contain this syntax still compile without issues. In case, you don't want the manual substitution to be included
during compilation, resulting in a pdf file with two versions of some lines, you can comment out all replacement
lines in the bottom part:

```latex
%@{
\textbf{Welcome to France!}
%@--
% \textit{Bienvenue en France !}
% $x < 3$
%@}
```

This still produces the aforementioned result but if you were to compile this LaTeX file you would only get your
original text in its result.

Lastly, you can write the same things twice in both parts of the block causing TransLaTeX to not translate, and
replace with the same thing, basically leaving parts of your file untouched by any operation, same as they were in
the beginning while other parts still being parsed and translated:

```latex
%@{
\textbf{Here is some gibberish sşaıdfajş}
%@--
% \textbf{Here is some gibberish sşaıdfajş}
%@}
```

After preprocessing, this results in:

```latex
\textbf{Here is some gibberish sşaıdfajş}
```

thus allowing you to keep certain parts untouched.

An interesting CLI option is `--no-pre` which disables the manual replacement in the preprocessor stage.

This still removes the blocks from translation but at the end, instead of replacing the whole block with the bottom
part,
it just recreates the block where it was, as it was, untouched, untranslated.

This allows you to test your file with or without the manual replacement that you have in your source file.

### Extra options

Here you will find details on some options mostly used for debugging during development, but that can still come in
handy for the end user on understanding what's going wrong while your file is being processed and how you can
potentially make it succeed.

* `-n` or `--dry-run`: This makes it so that no API call is made, no internet is used and TransLaTeX
  runs offline. This means that no translation is made but the pipeline is run up until the translation stage
  including parsing and tokenization. This helps to test the inner workings of TransLaTeX and especially the
  idempotency. Since the same contents of the given file is returned, one can check for differences. If you are using
  a paid API with limits, you can use this option to detect undetected errors in the processing of your file before
  calling for a real translation.
* `-d` or `--debug`: This is the debug option, and it does multiple things. Firstly, it enables the output of logs
  of level `DEBUG` or higher to `stderr`. This is the ultimate option as far as logs compared to `-v` and `-vv` since
  this also enables logs for TransLaTeX and for the imported modules while lowering the log level resulting in even more
  information. Secondly, it generates intermediary files produced while the input is being processed. These include the
  preprocessed, marked and tokenized versions of your given file, each relative
  to their respective stages and also the dictionaries that hold the markers and tokens and their associated LaTeX
  structures that they replace. This can give huge insight on what went on when TransLaTeX ran on your given file
  and what maybe went wrong.
* `-s` or `--stop`: This option takes an argument and enables you to stop TransLaTeX's execution at a given stage.
  Once stopped, that stage completes its operation and writes its result to the output file if specified or else to
  `stdout`. This can help you hunt down where a problem appears during the process.

```{note}
Take a look at the [](modules/index.md) section for even more details on the inner workings and the
architecture of TransLaTeX.
```

### Customizing behaviour

You can customize and improve TransLaTeX's behaviour by modifying or more importantly adding to the list of known
LaTeX structures in the {mod}`~translatex.data` module.

The default behaviour of TransLaTeX is dependent on the type of LaTeX structure encountered.

* For LaTeX **commands**:

```latex
\LaTeX
\TeX{}
\textbf{Bold text}
\href{https://www.overleaf.com/}{Link to Overleaf}
\url{https://www.overleaf.com/}
\madeupcommand[with][options]{and}{many}{arguments}[last option]
```

it is to tokenize everything except the very last occurring argument (last set of curly braces `{}`) since this
seems to be a common place to find the text that needs translation inside LaTeX commands even though not standard
for all commands.

Some commands that are known to never contain text to translate are tokenized as a whole
including all their arguments and options, like in the case for the `\url` command. This would for example produce
the following, before sending out for translation:

```text
[0-2]
[0-3]{}
[0-4]{Bold text}
[0-5]{Link to Overleaf}
[0-1]
[0-6]{arguments}
```

* For LaTeX **environments**:

```latex
\begin{document}
    \section{New section}
    This is some text.
    \(x < 0 \textnormal{some text inside an inline math environment}\)
    \begin{lstlisting}[language=Python]
    import numpy as np
    print("Hello, world!")
    \end{lstlisting}
    \begin{enumerate}
        \item Foo bar
        \item $ x < 0 $
        \item Spam eggs
    \end{enumerate}
    \[
        D=P^{-1}AP.
        \textsf{some text inside a block math environment}
    \]
    \begin{equation}
        A=\left[
            \begin{array}{ccc}
                3  & 3  & 4   \\
                6  & -2 & -12 \\
                -2 & 3  & 9
            \end{array}
            \right].\label{eq:A}
    \end{equation}
\end{document}
```

it is to tokenize the `\begin`/`\end` statements and recurse into the environment to find and process the nested
commands and environments if it is a regular environment. If it is a **math** environment, it is recursed into only
if it contains text to translate (any known commands that can contain text inside a math environment), otherwise, it
is tokenized as a whole. This is also true for environments that are known to never contain any text to translate,
they are tokenized as a whole, like in the case for `\begin{lstlisting}`. This produces the following result after
tokenization:

```text
[0-10]
  [0-7]{New section}
  This is some text.
  [0-2][0-8]{some text inside an inline math environment}[0-5]
  [0-11]
  [0-12]
    [0-1] Foo bar
    [0-1] [0-3]
    [0-1] Spam eggs
  [0-14]
  [0-4][0-9]{some text inside a block math environment}
  [0-6]
  [0-13]
[0-15]
```

So here is a relatively user-friendly way of customizing and altering these default behaviours of TransLaTeX to make
your file process correctly:

* Add the names of the LaTeX commands or environments in {data}`~translatex.data.COMPLETELY_REMOVED_COMMANDS` or
  {data}`~translatex.data.COMPLETELY_REMOVED_ENVS` respectively that are to be completely removed, and that never
  contain any text to translate.
* Add the names of the LaTeX **math** environments in {data}`~translatex.data.MATH_ENVS` for them to be processed as
  such. Add the names of any LaTeX commands used to insert text inside math environments in
  {data}`~translatex.data.TEXT_COMMANDS` for them to be detected and prepared for translation.
* Add the names of the LaTeX commands in {data}`~translatex.data.SPECIAL_COMMANDS` that are to be handled during the
  tokenization stage via regular expressions instead of during the marking stage via a parser. This is handy for
  complex and variable structures that need finer handling to be able to extract their text every time. Since
  entering in additional regex by the end user hasn't been implemented yet, anything you add here will only be
  skipped on all stages leaving these commands and all their arguments and options intact before sending out for
  translation (they could thus get altered by the translator resulting in a broken LaTeX file).

### Custom translation service

You can provide your own translation service by creating a python file containing one or several custom translation
service classes that derive from {class}`~translatex.translator.TranslationService` and
implement the {meth}`~translatex.translator.TranslationService.translate` method.

Suppose that a `custom.py` file contains the following code:

```{literalinclude} ../../tests/custom.py
```

Then, you can use it with the `--custom_api` option together with the `--service` option:

```bash
translatex --custom_api custom.py --service "Do not translate" input.tex output.tex
```

Here is another example with a custom translation service that uses the TextSynth API:

```{literalinclude} examples/textsynth.py
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
