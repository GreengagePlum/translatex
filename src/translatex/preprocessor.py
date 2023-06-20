import re
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from translatex.marker import Marker


class Preprocessor:
    DEFAULT_INITIAL_INDICATOR_INDEX: int = 0
    DEFAULT_INDICATOR_FORMAT: str = "%@=TRANSLATEX_MANUAL_REPLACEMENT_{}"
    DEFAULT_REPLACEMENT_BLOCK_BEGIN: str = "%@{"
    DEFAULT_REPLACEMENT_BLOCK_END: str = "%@}"
    DEFAULT_REPLACEMENT_BLOCK_SEPERATOR: str = "%@--"

    def __init__(self, latex: str) -> None:
        """Creates a Preprocessor with default settings.

        Args:
            latex: The string that contains LaTeX

        """
        self._base_latex: str = latex
        self._unprocessed_latex: str = latex
        self._processed_latex: str = str()
        self.indicator_count: int = Preprocessor.DEFAULT_INITIAL_INDICATOR_INDEX
        """Numbering used in the indicators. Its initial value represents -> first indicator number - 1."""
        self.indicator_format: str = Preprocessor.DEFAULT_INDICATOR_FORMAT
        self._indicator_store: Dict[int, str] = dict()
        """The dictionary that associates to each indicator the corresponding "manual substitution block" string it 
        replaces."""

    def update_from_marker(self, marker: "Marker") -> None:
        """A convenience method to update the processed LaTeX from a Marker."""
        self.processed_latex = marker.unmarked_latex

    def __str__(self) -> str:
        return "The indicator format is {} and indicator count is at {}.".format(self._indicator_format,
                                                                                 self.indicator_count)

    def _next_indicator(self) -> str:
        self.indicator_count += 1
        return self.indicator_format.format(self.indicator_count)

    @property
    def unprocessed_latex(self) -> str:
        """Unprocessed, correct LaTeX string

        If this property is set, processed string, and all preprocessor related stuff gets reset so that everything is
        in sync
        """
        return self._unprocessed_latex

    @unprocessed_latex.setter
    def unprocessed_latex(self, latex: str) -> None:
        self._unprocessed_latex = latex
        self._processed_latex = str()
        self.indicator_count = Preprocessor.DEFAULT_INITIAL_INDICATOR_INDEX
        self._indicator_store = dict()

    @property
    def processed_latex(self) -> str:
        """Processed, ready to mark string after preprocessing operations.

        If this property is set, unprocessed string gets reset so that everything is in sync
        """
        return self._processed_latex

    @processed_latex.setter
    def processed_latex(self, latex: str) -> None:
        self._processed_latex = latex
        self._unprocessed_latex = str()

    @property
    def base_latex(self) -> str:
        """The starting LaTeX string. Saved aside so the original source is kept intact and accessible if need be.

        If the base changes, almost everything is reset and readied for the new base so that everything is in sync
        """
        return self._base_latex

    @base_latex.setter
    def base_latex(self, latex: str) -> None:
        self._base_latex = self._unprocessed_latex = latex
        self._processed_latex = str()
        self.indicator_count = Preprocessor.DEFAULT_INITIAL_INDICATOR_INDEX
        self._indicator_store = dict()

    @property
    def indicator_format(self) -> str:
        """The format string for indicators to be used.

        Raises:
            ValueError: If the given string doesn't have at least a single occurrence of a pair of empty curly
                braces "{}". Since we're looking for a string that can be used with ``str.format()``

        """
        return self._indicator_format

    @indicator_format.setter
    def indicator_format(self, format_str: str) -> None:
        pattern = r'\{\}'
        match = re.search(pattern, format_str)
        if not match:
            raise ValueError("No empty curly braces in the given format string")
        self._indicator_format = format_str

    def process(self) -> None:
        current_string = self._unprocessed_latex
        pattern = re.compile(re.escape(Preprocessor.DEFAULT_REPLACEMENT_BLOCK_BEGIN) + r".*" + re.escape(
            Preprocessor.DEFAULT_REPLACEMENT_BLOCK_SEPERATOR) + r".*" + re.escape(
            Preprocessor.DEFAULT_REPLACEMENT_BLOCK_END), re.DOTALL)
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                self._indicator_store.update({self.indicator_count + 1: match[0]})
                current_string, _ = pattern.subn(self._next_indicator(), current_string, 1)
            else:
                all_replaced = True
        self._processed_latex = current_string

    def rebuild(self, enable_substitution: bool = True) -> None:
        current_string = self._processed_latex
        pattern = re.compile(re.escape(Preprocessor.DEFAULT_REPLACEMENT_BLOCK_SEPERATOR) + r".*\n([\s\S]*)\n" +
                             re.escape(Preprocessor.DEFAULT_REPLACEMENT_BLOCK_END))
        for indicator, value in self._indicator_store.items():
            replacement_string = value
            if enable_substitution:
                replacement_string = pattern.match(replacement_string).group(1)
            current_string = current_string.replace(self._indicator_format.format(indicator), replacement_string)
        self._unprocessed_latex = current_string


if __name__ == "__main__":
    base_file = "translatex"
    with open(f"../../examples/{base_file}.tex") as f:
        p = Preprocessor(f.read())

    p.process()
    with open(f"../../examples/{base_file}_post.tex", "w+") as f:
        f.write(p.processed_latex)

    p.rebuild()
    with open(f"../../examples/{base_file}_post2.tex", "w+") as f:
        f.write(p.unprocessed_latex)
