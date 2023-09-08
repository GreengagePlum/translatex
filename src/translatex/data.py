from typing import List

MATH_ENVS: List[str] = [
    "$",
    "$$",
    "math",
    "displaymath",
    "equation",
    "equation*",
    "cases",
    "array",
    "matrix",
    "pmatrix",
    "bmatrix",
    "Bmatrix",
    "vmatrix",
    "Vmatrix",
]
"""These are the names of the known LaTeX math environments to the program.

This list is used to determine math environments and stop recursion inside them to be able to mark their whole contents
once if no text command is found inside. This helps us generate way less marks and thus subsequently, less tokens which
potentially makes the final output less confusing for the automatic translator.
"""
COMPLETELY_REMOVED_ENVS: List[str] = [
    "verbatim",
    "verbatim*",
    "lstlisting",
    "tikzpicture",
]
"""These are the names of the known named environments to the program to be completely marked and tokenized.

This list is used to determine environments which contain literal text or are unsupported so that their contents
don't get recursed into and that they get marked with a single marker resulting in none of their contents being
prepared for translation.
"""

TEXT_COMMANDS: List[str] = [
    "text",
    "texttt",
    "textsf",
    "textrm",
    "textnormal",
    "mbox",
]
"""These are the names of the known LaTeX text commands to the program.

This list contains the commands that can be used inside math environments to enter regularly typeset text. The
contents of these commands need translation so they shouldn't be removed. This list is used to stop the math
environment processor from including these commands in its marking.
"""
SPECIAL_COMMANDS: List[str] = [
    "draw",
    "fill",
    "filldraw",
    "node",
    "verb",
    "item",
]
"""These are commands that need a special regex treatment to extract their text."""
COMPLETELY_REMOVED_COMMANDS: List[str] = [
    "label",
    "ref",
    "cite",
    "pageref",
    "url",
    "lstinputlisting",
    "inputencoding",
    "bibliography",
    "bibliographystyle",
    "setlength",
    "color",
    "pagecolor",
    "input",
    "includegraphics",
    "rule",
]
"""These are commands that need to be completely tokenized and that never have text to be translated inside."""
SKIPPED_COMMANDS: List[str] = SPECIAL_COMMANDS + COMPLETELY_REMOVED_COMMANDS
"""These are the names of the known LaTeX commands to the program that require special attention.

These commands are left unmarked so that later passes that use regex can handle them more correctly. Most are commands
that never contain text to be translated, but some are also highly complicated or conditional so they require more
intricate regex treatment.
"""
