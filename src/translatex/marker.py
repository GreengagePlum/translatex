"""This is the marker module where the LaTeX parse tree operations are made.

This module houses all the logic and information necessary to mark all LaTeX structures to be tokenized in later
passes except for the skipped commands. It is designed for internal use to the program, but it can be used standalone
to see its workings.

This module makes heavy use of the TexSoup module to have a LaTeX parse tree and recurse into substructures. All
structures that need to be tokenized later are marked recursively so that the tokenization pass can be simpler and
compatible with many more types of structures.
"""
import re
from typing import Dict, List, Optional

from TexSoup import TexSoup
from TexSoup.data import *

MATH_ENVS: List[str] = ["$", "$$", "math", "displaymath", "equation", "equation*", "cases", "array", "matrix",
                        "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix"]
"""These are the names of the known LaTeX math environments to the program.

This list is used to determine math environments and stop recursion inside them to be able to mark their whole contents
once if no text command is found inside. This helps us generate way less marks and thus subsequently, less tokens which
potentially makes the final output less confusing for the automatic translator.
"""
CODE_ENVS: List[str] = ["verbatim", "verbatim*", "lstlisting"]
"""These are the names of the known LaTeX literal environments to the program.

This list is used to determine environments which contain source code so that their contents don't get recursed into and
that they get marked with a single marker resulting in none of their contents being prepared for translation.
"""

TEXT_COMMANDS: List[str] = ["text", "texttt", "textsf", "textrm", "textnormal", "mbox"]
"""These are the names of the known LaTeX text commands to the program.

This list contains the commands that can be used inside math environments to enter regularly typeset text. The 
contents of these commands need translation so they shouldn't be removed. This list is used to stop the math 
environment processor from including these commands in its marking.
"""
SKIPPED_COMMANDS: List[str] = ["label", "ref", "cite", "href", "hyperlink", "hypertarget", "pageref", "url",
                               "inputencoding", "verb", "lstinputlisting", "bibliography", "bibliographystyle",
                               "includegraphics", "setlength", "color", "pagecolor", "rule", "textcolor", "colorbox",
                               "draw", "fill", "filldraw", "node"]
"""These are the names of the known LaTeX commands to the program that require special attention.

These commands are left unmarked so that later passes that use regex can handle them more correctly. Most are commands
that never contain text to be translated, but some are also highly complicated or conditional so they require more
intricate regex treatment.
"""


class Marker:
    """This class traverses the LaTeX syntax tree and recursively marks structures to be tokenized later.

    The parse tree is constructed and traversed using TexSoup and its methods.
    """

    def __init__(self, latex: str) -> None:
        """Creates a Marker with default settings.

        Args:
            latex: The string that contains LaTeX

        """
        self.soup_original: TexNode = TexSoup(latex)
        """The starting LaTeX tree. Saved aside so the original source is kept intact."""
        self.soup_current: TexNode = TexSoup(latex)
        """The current working LaTeX tree. Marking manipulations are done here."""
        self.marker_count: int = 0
        """Numbering used in the markers. Its value represents -> first marker number - 1."""
        self.marker_format: str = "//{}//"
        """The format string for markers to be used."""
        self.marker_store: Dict[int, str] = dict()
        """The dictionary that associates to each marker the corresponding string it replaces."""

    def __str__(self) -> str:
        return str(self.soup_current)

    def __next_marker(self) -> str:
        self.marker_count += 1
        return self.marker_format.format(self.marker_count)

    @property
    def marker_format(self) -> str:
        return self.marker_format

    @marker_format.setter
    def marker_format(self, format_str: str) -> None:
        """Set marker format to be used.

        Args:
            format_str: A string that can be used with ``.format()``

        Raises:
            ValueError: If the given string doesn't have at least a single occurrence of two empty curly braces "{}"

        """
        pattern = r'\{\}'
        match = re.search(pattern, format_str)
        if not match:
            raise ValueError("No empty curly braces in the given format string")
        self.marker_format = format_str

    def __mark_node_name(self, node: TexNode) -> None:
        previous_name: str = str(node.name)
        if type(node.expr) is TexNamedEnv:
            node.name = self.__next_marker()
            self.marker_store.update({self.marker_count: previous_name})
        elif type(node.expr) is TexCmd:
            if node.name in SKIPPED_COMMANDS:
                return
            node.name = self.__next_marker()
            self.marker_store.update({self.marker_count: previous_name})

    def __mark_node_contents(self, node: TexNode, original_expression_size: int = 0,
                             replace_range: range = None) -> None:
        # TODO: Test if lists need deep copying
        if (original_expression_size != 0) ^ (replace_range is not None):
            raise ValueError("Either supply both optional parameters or none of them")
        if original_expression_size == 0 and replace_range is None:
            previous_expression: list = node.expr.all
            # Sanitize previous expressions so that it no longer contains command options within []
            args = [y.pop() for y in [x.contents for x in node.args if type(x) is BracketGroup]]
            previous_expression = [x for x in previous_expression if x not in args]
            node.contents = [self.__next_marker()]
            self.marker_store.update({self.marker_count: "".join([str(x) for x in previous_expression])})
        else:
            current_expression_size = len(node.expr.all)
            adjustment_difference = original_expression_size - current_expression_size
            adjusted_replace_range = range(replace_range.start - adjustment_difference,
                                           replace_range.stop - adjustment_difference)
            previous_expression: list = node.expr.all[adjusted_replace_range.start:adjusted_replace_range.stop]
            # Sanitize previous expressions so that it no longer contains command options within []
            args = [y.pop() for y in [x.contents for x in node.args if type(x) is BracketGroup]]
            previous_expression = [x for x in previous_expression if x not in args]
            new_contents = list(node.expr.all)
            del new_contents[adjusted_replace_range.start:adjusted_replace_range.stop]
            new_contents.insert(adjusted_replace_range.start, self.__next_marker())
            node.contents = new_contents
            self.marker_store.update({self.marker_count: "".join([str(x) for x in previous_expression])})

    @staticmethod
    def __marking_range_finder(node: TexNode, excluded_commands: List[str]) -> List[range]:
        ranges_to_mark: List[range] = list()
        start: int = -1
        for i, expr in enumerate(node.expr.all):
            if start == -1 and (type(expr) is not TexCmd or expr.name not in excluded_commands):
                start = i
            elif start != -1 and type(expr) is TexCmd and expr.name in excluded_commands:
                ranges_to_mark.append(range(start, i))
                start = -1
            elif len(node.expr.all) - 1 == i:
                ranges_to_mark.append(range(start, i + 1))
        return ranges_to_mark

    def __math_processor(self, node: TexNode) -> Optional[TexNode]:
        continue_recursion = False
        for descendant in node.descendants:
            if type(descendant) is TexNode and descendant.name in TEXT_COMMANDS:
                continue_recursion = True
                break
        if continue_recursion:
            ranges_to_mark: List[range] = self.__marking_range_finder(node, TEXT_COMMANDS)
            original_expression_size: int = len(node.expr.all)
            for range_to_mark in ranges_to_mark:
                self.__mark_node_contents(node, original_expression_size, range_to_mark)
        else:
            self.__mark_node_contents(node)
            # TODO: implement way to completely mark and replace named math environment (maybe)
        if type(node.expr) is TexNamedEnv:
            self.__mark_node_name(node)
        return node if continue_recursion else None

    def __traverse_ast_aux(self, node: TexNode) -> None:
        if node.name in MATH_ENVS:
            marked_node: Optional[TexNode] = self.__math_processor(node)
            if marked_node:
                for current_node in marked_node.children:
                    self.__traverse_ast_aux(current_node)
        elif node.name in CODE_ENVS:
            self.__mark_node_contents(node)
            self.__mark_node_name(node)
        elif len(node.children) == 0:
            self.__mark_node_name(node)
        else:
            for current_node in node.children:
                self.__traverse_ast_aux(current_node)
            self.__mark_node_name(node)

    def traverse_ast(self):
        # Start marking inside and including "\begin{document}" (headers untouched)
        self.__traverse_ast_aux(self.soup_current.find("document"))

    def undo_marking(self) -> str:
        latex: str = str(self)
        for marker, value in self.marker_store.items():
            pattern = r"//{}//".format(marker)
            latex = latex.replace(pattern, value)
        return latex


# with open("../../examples/translatex.tex") as f:
#     m = Marker(f.read())

# m = Marker(r"""
# \begin{document}
# \textbf{\color{\text{blue}} Hello world}
# \end{document}
# """)
# m.traverse_ast()
# for value in m.marker_store.values():
#     print(type(value))

# m.traverse_ast()

# with open("../../examples/translatex_post.tex", "w+") as f:
#     f.write(str(m))

# final_string = m.undo_marking()
# with open("../../examples/translatex_post.tex", "w+") as f:
#     f.write(final_string)

# print(str(m))

# import sys
# if __name__ == "__main__":
#     sys.exit(0)  # pragma: no cover
