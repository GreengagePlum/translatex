"""This is the marker module where the LaTeX parse tree operations are made.

This module houses all the logic and information necessary to mark all LaTeX structures to be tokenized in later
passes except for the skipped commands. It is designed for internal use to the program, but it can be used standalone
to see its workings.

This module makes heavy use of the TexSoup module to have a LaTeX parse tree and recurse into substructures. All
structures that need to be tokenized later are marked recursively so that the tokenization pass can be simpler and
compatible with many more types of structures.
"""
import logging
import re
from typing import TYPE_CHECKING, Dict, Optional

from TexSoup import TexSoup
from TexSoup.data import *

from .data import *
from .preprocessor import Preprocessor

if TYPE_CHECKING:
    from .tokenizer import Tokenizer

log = logging.getLogger("translatex.marker")


class Marker:
    """This class traverses the LaTeX syntax tree and recursively marks structures to be tokenized later.

    The parse tree is constructed and traversed using TexSoup and its methods.
    TexSoup's best effort fault tolerance mode for parsing LaTeX is not used.
    """

    DEFAULT_INITIAL_MARKER_INDEX: int = 0
    DEFAULT_MARKER_FORMAT: str = "//{}//"

    def __init__(self, latex: str) -> None:
        """Creates a Marker with default settings.

        Args:
            latex: The string that contains LaTeX

        """
        self._base_latex: str = latex
        self._unmarked_latex: str = latex
        self._marked_latex: str = str()
        self.marker_count: int = Marker.DEFAULT_INITIAL_MARKER_INDEX
        """Numbering used in the markers. Its initial value represents -> first marker number - 1."""
        self.marker_format: str = Marker.DEFAULT_MARKER_FORMAT
        self._marker_store: Dict[int, str] = dict()
        """The dictionary that associates to each marker the corresponding string it replaces."""

    @classmethod
    def from_preprocessor(cls, preprocessor: Preprocessor) -> "Marker":
        """Another constructor that creates a Marker from a given Preprocessor. For convenience."""
        return cls(preprocessor.processed_latex)

    def update_from_tokenizer(self, tokenizer: "Tokenizer") -> None:
        """A convenience method to update the marked LaTeX from a Tokenizer."""
        self.marked_latex = tokenizer.marked_string

    def __str__(self) -> str:
        return f"The marker format is {self._marker_format} and marker count is at {self.marker_count}."

    def _next_marker(self) -> str:
        self.marker_count += 1
        return self.marker_format.format(self.marker_count)

    @property
    def unmarked_latex(self) -> str:
        """Unmarked, correct LaTeX string

        If this property is set, marked string, and all marker related stuff gets reset so that everything is in
        sync
        """
        return self._unmarked_latex

    @unmarked_latex.setter
    def unmarked_latex(self, latex: str) -> None:
        self._unmarked_latex = latex
        self._marked_latex = str()
        self.marker_count = Marker.DEFAULT_INITIAL_MARKER_INDEX
        self._marker_store = dict()

    @property
    def marked_latex(self) -> str:
        """Marked, ready to tokenize string after marking operations.

        If this property is set, unmarked string gets reset so that everything is in sync
        """
        return self._marked_latex

    @marked_latex.setter
    def marked_latex(self, latex: str) -> None:
        self._marked_latex = latex
        self._unmarked_latex = str()

    @property
    def base_latex(self) -> str:
        """The starting LaTeX string. Saved aside so the original source is kept intact and accessible if need be.

        If the base changes, almost everything is reset and readied for the new base so that everything is in sync
        """
        return self._base_latex

    @base_latex.setter
    def base_latex(self, latex: str) -> None:
        self._base_latex = self._unmarked_latex = latex
        self._marked_latex = str()
        self.marker_count = Marker.DEFAULT_INITIAL_MARKER_INDEX
        self._marker_store = dict()

    @property
    def marker_format(self) -> str:
        """The format string for markers to be used.

        Raises:
            ValueError: If the given string doesn't have at least a single occurrence of a pair of empty curly
                braces "{}". Since we're looking for a string that can be used with ``str.format()``

        """
        return self._marker_format

    @marker_format.setter
    def marker_format(self, format_str: str) -> None:
        Marker.marker_format_check(format_str)
        self._marker_format = format_str

    @staticmethod
    def marker_format_check(format_str: str) -> None:
        pattern = r"\{\}"
        match = re.search(pattern, format_str)
        if not match:
            raise ValueError(
                "No empty curly braces in the given format string"
            )

    @staticmethod
    def marker_regex(format_str: str) -> str:
        """Construct a regex corresponding to the given marker format."""
        Marker.marker_format_check(format_str)
        curly_start = format_str.find(r"{}")
        escaped_marker_format = (
            re.escape(format_str[:curly_start])
            + "{}"
            + re.escape(format_str[curly_start + 2 :])
        )
        return escaped_marker_format.format(r"(?:\d+)")

    def dump_store(self) -> str:
        string_transformed = [
            f"{item}\n" for item in self._marker_store.items()
        ]
        return "".join(string_transformed)

    def _marker_regex(self) -> str:
        """Construct a regex corresponding to the current instance marker format."""
        return Marker.marker_regex(self._marker_format)

    def _mark_node_name(self, node: TexNode) -> None:
        """This method replaces a TexNode's name attribute with a marker and saves the replaced string in the
        dictionary.

        Named environments have their curly braces marked while commands have their name after the backslash marked.
        This is due to TexSoup behaviour.

        .. note::
            The names of the skipped commands are kept intact but recursion inside them continues.

        Args:
            node: A node in the TexSoup syntax tree

        """
        previous_name: str = str(node.name)
        if type(node.expr) is TexNamedEnv:
            node.name = self._next_marker()
            self._marker_store.update({self.marker_count: previous_name})
        elif type(node.expr) is TexCmd:
            if node.name in SKIPPED_COMMANDS:
                return
            node.name = self._next_marker()
            self._marker_store.update({self.marker_count: previous_name})

    def _mark_node_contents(
        self,
        node: TexNode,
        original_expression_size: int = 0,
        replace_range: range = None,
    ) -> None:
        """This method marks the contents of a TexNode. It is used for LaTeX environments rather than commands.

        If no optional parameters are passed, all the contents get marked with a single marker. If both optional
        parameters are specified, only the given ranges are marked and the rest is left as is for further treatment and
        recursion. All the parts that the marker replaces are turned into strings and stored in the dictionary.
        Any LaTeX bracket arguments are removed from the marking process so that they can be processed with
        regex during tokenization run.

        .. note::
            Either provide both optional arguments or none.

        Args:
            node: A node in the TexSoup syntax tree
            original_expression_size: The starting length of the TexSoup expression list for this node. Used to adjust
            the given ranges for the removals done to the list.
            replace_range: A range in the list of expressions to mark

        """
        if (original_expression_size != 0) ^ (replace_range is not None):
            raise ValueError(
                "Either supply both optional parameters or none of them"
            )
        if original_expression_size == 0 and replace_range is None:
            previous_expression: list = node.expr.all
            # Sanitize previous expressions so that it no longer contains command options within []
            args = [
                y.pop()
                for y in [
                    x.contents for x in node.args if type(x) is BracketGroup
                ]
            ]
            previous_expression = [
                x for x in previous_expression if x not in args
            ]
            node.contents = [self._next_marker()]
            self._marker_store.update(
                {
                    self.marker_count: "".join(
                        [str(x) for x in previous_expression]
                    )
                }
            )
        else:
            current_expression_size = len(node.expr.all)
            adjustment_difference = (
                original_expression_size - current_expression_size
            )
            adjusted_replace_range = range(
                replace_range.start - adjustment_difference,
                replace_range.stop - adjustment_difference,
            )
            previous_expression: list = node.expr.all[
                adjusted_replace_range.start : adjusted_replace_range.stop
            ]
            # Sanitize previous expressions so that it no longer contains command options within []
            args = [
                y.pop()
                for y in [
                    x.contents for x in node.args if type(x) is BracketGroup
                ]
            ]
            previous_expression = [
                x for x in previous_expression if x not in args
            ]
            new_contents = list(node.expr.all)
            del new_contents[
                adjusted_replace_range.start : adjusted_replace_range.stop
            ]
            new_contents.insert(
                adjusted_replace_range.start, self._next_marker()
            )
            node.contents = new_contents
            self._marker_store.update(
                {
                    self.marker_count: "".join(
                        [str(x) for x in previous_expression]
                    )
                }
            )

    @staticmethod
    def _marking_range_finder(
        node: TexNode, excluded_commands: List[str]
    ) -> List[range]:
        """Finds ranges to be replaced with markers in the list of expressions of a node according to the given
        exclude list.

        Any excluded commands are kept as is and anything else is counted in ranges and returned. This is a static
        method and doesn't modify any of its arguments (read-only), it's just a calculation method.

        .. warning::

            For now, the excluded commands are searched only one level deep in the children of the node, leaving
            excluded commands appearing in nested structures ignored, thus them getting included in the ranges produced.

        Args:
            node: A node in the TexSoup syntax tree
            excluded_commands: A list of strings indicating the names of the LaTeX commands to leave outside the
            calculated ranges.

        Returns:
            A list of ranges corresponding to the expression list of the given node.

        """
        # TODO: make it work recursively so that commands more than one level deep aren't ignored.
        ranges_to_mark: List[range] = list()
        start: int = -1
        for i, expr in enumerate(node.expr.all):
            if start == -1 and (
                type(expr) is not TexCmd or expr.name not in excluded_commands
            ):
                start = i
            elif (
                start != -1
                and type(expr) is TexCmd
                and expr.name in excluded_commands
            ):
                ranges_to_mark.append(range(start, i))
                start = -1
            elif len(node.expr.all) - 1 == i:
                ranges_to_mark.append(range(start, i + 1))
        return ranges_to_mark

    def _math_processor(self, node: TexNode) -> Optional[TexNode]:
        """This method is made to handle the LaTeX math environments.

        The special treatment here is as follows. If a text command inside the math environment is found, the contents
        of this environment is marked by calculating the ranges where there are no text commands so that they are marked
        with a single marker optimizing the produced number of markers which may be substantially high otherwise for no
        good reason, potentially making tokenization harder and confusing the automatic translater at the end. If no text
        command is found, all contents are marked with a single marker and recursion is stopped.

        .. note::

            If the given node is a named environment, its name is also marked at the end.

        Args:
            node: A node in the TexSoup syntax tree

        Returns:
            Either the given TexNode or None depending on if recursion inside needs to continue or not.

        """
        continue_recursion = False
        for descendant in node.descendants:
            if (
                type(descendant) is TexNode
                and descendant.name in TEXT_COMMANDS
            ):
                continue_recursion = True
                break
        if continue_recursion:
            ranges_to_mark: List[range] = self._marking_range_finder(
                node, TEXT_COMMANDS
            )
            original_expression_size: int = len(node.expr.all)
            for range_to_mark in ranges_to_mark:
                self._mark_node_contents(
                    node, original_expression_size, range_to_mark
                )
        else:
            self._mark_node_contents(node)
            # TODO: implement way to completely mark and replace named math environment (maybe)
        if type(node.expr) is TexNamedEnv:
            self._mark_node_name(node)
        return node if continue_recursion else None

    def _traverse_ast(self, node: TexNode) -> None:
        """This is where the recursive, depth-first tree traversal takes place.

        Every node and their children are treated in a depth-first manner. If there is a math environment, it is sent
        for special treatment. If it's a code environment, its contents are completely marked and recursion inside it is
        stopped. Otherwise, it is sent for normal marking.

        Args:
            node: A node in the TexSoup syntax tree

        """
        if node.name in MATH_ENVS:
            marked_node: Optional[TexNode] = self._math_processor(node)
            if marked_node:
                for current_node in marked_node.children:
                    self._traverse_ast(current_node)
        elif node.name in COMPLETELY_REMOVED_ENVS:
            self._mark_node_contents(node)
            self._mark_node_name(node)
        elif len(node.children) == 0:
            self._mark_node_name(node)
        else:
            for current_node in node.children:
                self._traverse_ast(current_node)
            self._mark_node_name(node)

    def mark(self) -> None:
        """This produces the marked LaTeX string from the unmarked string if
        available.

        It is assumed correct LaTeX that can be compiled without issues
        otherwise TexSoup parsing will produce errors.

        The marked string is stored in an instance variable at the end.

        Raises:
            ValueError: If string to mark is empty.

        """
        if self._unmarked_latex:
            soup_current: TexNode = TexSoup(self._unmarked_latex)
            # Start marking inside and including "\begin{document}"
            # (headers untouched)
            document = soup_current.find("document")
            if document is None:
                # there is no document environment,
                # so we assume the whole text is the body
                self._traverse_ast(soup_current)
            else:
                self._traverse_ast(document)
            self._marked_latex = str(soup_current)

        else:
            raise ValueError("Unmarked string is empty, nothing to mark")

    def unmark(self) -> None:
        """This uses the marker store to rebuild the unmarked string.

        The dictionary is iterated through and each marker is replaced with its associated LaTeX string. At the end, the
        unmarked string is stored in an instance variable.

        Write logs on encounter of any missing or altered markers in the string to unmark.

        Raises:
            LookupError: If a marker is found to be missing in the processed string.
            ValueError: If string to unmark is empty.

        """
        current_string: str = self._marked_latex
        if not current_string:
            raise ValueError("Marked string is empty, nothing to unmark")
        for marker, value in self._marker_store.items():
            formatted_marker = self._marker_format.format(marker)
            if current_string.count(formatted_marker) == 0:
                log.error(
                    f"Found missing or altered MARKER: {formatted_marker} --> during stage MARKER"
                )
            else:
                current_string = current_string.replace(
                    formatted_marker, value
                )
        self._unmarked_latex = current_string
