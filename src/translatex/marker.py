from typing import Dict, List, Optional

from TexSoup import TexSoup
from TexSoup.data import *

MATH_ENVS: List[str] = ["$", "$$", "math", "displaymath", "equation", "equation*", "cases", "array", "matrix",
                        "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix"]
CODE_ENVS: List[str] = ["verbatim", "verbatim*", "lstlisting"]
TEXT_COMMANDS: List[str] = ["text", "texttt", "textsf", "textrm", "textnormal", "mbox"]
SKIPPED_COMMANDS: List[str] = ["label", "ref", "cite", "href", "hyperlink", "hypertarget", "pageref", "url",
                               "inputencoding", "verb", "lstinputlisting", "bibliography", "bibliographystyle",
                               "includegraphics", "setlength", "color", "pagecolor", "rule", "textcolor", "colorbox",
                               "draw", "fill", "filldraw", "node"]


class Marker:

    def __init__(self, latex: str) -> None:
        self.soup_original: TexNode = TexSoup(latex)
        self.soup_current: TexNode = TexSoup(latex)
        self.marker_count: int = 0
        self.marker_format: str = "//{}//"
        self.marker_store: Dict[int, str | list] = dict()

    def __str__(self) -> str:
        return str(self.soup_current)

    def __next_marker(self) -> str:
        self.marker_count += 1
        return self.marker_format.format(self.marker_count)

    def set_marker_format(self, format_str: str) -> None:
        # TODO: implement format string check (if it has only a single occurrence of "{}")
        self.marker_format = format_str

    def __mark_node_name(self, node: TexNode) -> None:
        previous_name: str = node.name
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

# with open("../../examples/translatex_post.tex", "w+") as f:
#     f.write(str(m))

# final_string = m.undo_marking()
# with open("../../examples/translatex_post.tex", "w+") as f:
#     f.write(final_string)

# print(str(m))

# import sys
# if __name__ == "__main__":
#     sys.exit(0)  # pragma: no cover
