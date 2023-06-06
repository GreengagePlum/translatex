from typing import Dict, List, Optional

from TexSoup import TexSoup
from TexSoup.data import *

MATH_ENVS: List[str] = ["$", "$$", "math", "displaymath", "equation", "equation*", "cases", "array", "matrix",
                        "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix"]
CODE_ENVS: List[str] = ["verbatim", "verbatim*", "lstlisting"]
TEXT_COMMANDS: List[str] = ["text", "textsf", "textrm", "textnormal"]
SKIPPED_COMMANDS: List[str] = ["label", "ref", "cite", "href", "hyperlink", "hypertarget", "pageref", "url",
                               "inputencoding", "verb", "lstinputlisting", "bibliography", "bibliographystyle"]


class Marker:

    def __init__(self, latex: str) -> None:
        self.soup: TexNode = TexSoup(latex)
        self.marker_count: int = 0
        self.marker_format: str = "//{}//"
        self.marker_store: Dict[int, str | list] = dict()

    def __str__(self) -> str:
        return str(self.soup)

    def __next_marker__(self) -> str:
        self.marker_count += 1
        return self.marker_format.format(self.marker_count)

    def set_marker_format(self, format_str: str) -> None:
        # TODO: implement format string check (if it has only a single occurrence of "{}")
        self.marker_format = format_str

    def __mark_node_name__(self, node: TexNode) -> None:
        previous_name: str = node.name
        if type(node.expr) is TexNamedEnv:
            node.name = self.__next_marker__()
            self.marker_store.update({self.marker_count: previous_name})
        elif type(node.expr) is TexCmd:
            if node.name in SKIPPED_COMMANDS:
                return
            node.name = self.__next_marker__()
            self.marker_store.update({self.marker_count: previous_name})

    def __mark_node_contents__(self, node: TexNode, original_contents_size: int = 0,
                               replace_range: range = None) -> None:
        # TODO: Test if lists need deep copying
        if (original_contents_size != 0) ^ (replace_range is not None):
            raise ValueError("Either supply both optional parameters or none of them")
        if original_contents_size == 0 and replace_range is None:
            previous_contents: list = node.contents
            # Sanitize previous contents so that it no longer contains command options within []
            args = [y.pop() for y in [x.contents for x in node.args if type(x) is BracketGroup]]
            previous_contents = [x for x in previous_contents if x not in args]
            node.contents = [self.__next_marker__()]
            self.marker_store.update({self.marker_count: "".join([str(x) for x in previous_contents])})
        else:
            current_contents_size = len(node.contents)
            adjustment_difference = original_contents_size - current_contents_size
            adjusted_replace_range = range(replace_range.start - adjustment_difference,
                                           replace_range.stop - adjustment_difference)
            previous_contents: list = node.contents[adjusted_replace_range.start:adjusted_replace_range.stop]
            # Sanitize previous contents so that it no longer contains command options within []
            args = [y.pop() for y in [x.contents for x in node.args if type(x) is BracketGroup]]
            previous_contents = [x for x in previous_contents if x not in args]
            new_contents = list(node.contents)
            del new_contents[adjusted_replace_range.start:adjusted_replace_range.stop]
            new_contents.insert(adjusted_replace_range.start, self.__next_marker__())
            # Turn every TexNode into a TexExpr since TexSoup wants it that way
            # this also updates the syntax tree and recursion into nodes stays possible
            new_contents = [x.expr if type(x) is TexNode else x for x in new_contents]
            node.contents = new_contents
            self.marker_store.update({self.marker_count: "".join([str(x) for x in previous_contents])})

    @staticmethod
    def __marking_range_finder__(node: TexNode, excluded_commands: List[str]) -> List[range]:
        ranges_to_mark: List[range] = list()
        start: int = -1
        for i, content in enumerate(node.contents):
            if start == -1 and (type(content) is not TexNode or content.name not in excluded_commands):
                start = i
            elif start != -1 and type(content) is TexNode and content.name in excluded_commands:
                ranges_to_mark.append(range(start, i))
                start = -1
            elif len(node.contents) - 1 == i:
                ranges_to_mark.append(range(start, i + 1))
        return ranges_to_mark

    def __math_processor__(self, node: TexNode) -> Optional[TexNode]:
        continue_recursion = False
        for descendant in node.descendants:
            if type(descendant) is TexNode and descendant.name in TEXT_COMMANDS:
                continue_recursion = True
                break
        if continue_recursion:
            ranges_to_mark: List[range] = self.__marking_range_finder__(node, TEXT_COMMANDS)
            original_contents_size: int = len(node.contents)
            for range_to_mark in ranges_to_mark:
                self.__mark_node_contents__(node, original_contents_size, range_to_mark)
        else:
            self.__mark_node_contents__(node)
            # TODO: implement way to completely mark and replace named math environment (maybe)
        if type(node.expr) is TexNamedEnv:
            self.__mark_node_name__(node)
        return node if continue_recursion else None

    def __traverse_ast_aux__(self, node: TexNode) -> None:
        if node.name in MATH_ENVS:
            marked_node: Optional[TexNode] = self.__math_processor__(node)
            if marked_node:
                for current_node in marked_node.children:
                    self.__traverse_ast_aux__(current_node)
        elif node.name in CODE_ENVS:
            self.__mark_node_contents__(node)
            self.__mark_node_name__(node)
        elif len(node.children) == 0:
            self.__mark_node_name__(node)
        else:
            for current_node in node.children:
                self.__traverse_ast_aux__(current_node)
            self.__mark_node_name__(node)

    def traverse_ast(self):
        # Start marking inside and including "\begin{document}" (headers untouched)
        self.__traverse_ast_aux__(self.soup.find("document"))

    def undo_marking(self) -> str:
        latex: str = str(self)
        for marker, value in self.marker_store.items():
            pattern = r"//{}//".format(marker)
            latex = latex.replace(pattern, value)
        return latex


with open("../../examples/erken.tex") as f:
    m = Marker(f.read())
m.traverse_ast()
final_string = m.undo_marking()
with open("../../examples/erken_post.tex", "w+") as f:
    f.write(final_string)
# print(str(m))
