"""This is where all the preparations are made before anything. TransLaTeX preprocessor syntax is handled here."""
import re
import sys
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from translatex.marker import Marker


class Preprocessor:
    """This class processes the preprocessor statements in the given LaTeX string.

    For the time being, the only statement is the manual substitution to avoid certain lines from getting tokenized and
    sent to translation. It offers a way to override the program's default behavior.

    In the future, the preprocessor statements can be extended further with new features to enable more fine-tuned
    control of the program's behavior by end users without them having to delve into source code.
    """
    DEFAULT_INITIAL_INDICATOR_INDEX: int = 0
    DEFAULT_INDICATOR_FORMAT: str = "%@=TRANSLATEX_MANUAL_REPLACEMENT_{}"
    """This indicator is used as a placeholder for manual replacement blocks, to keep track of its location."""
    DEFAULT_OPERATION_STAMP: str = "%@=Manual intervention by TransLaTeX"
    """This indicator is used to annotate the final LaTeX string with the operation made at that location
    (for end users to have more information)."""
    DEFAULT_REPLACEMENT_BLOCK_BEGIN: str = "%@{"
    """Default preprocessor syntax to indicate the start of a TransLaTeX replacement block."""
    DEFAULT_REPLACEMENT_BLOCK_END: str = "%@}"
    """Default preprocessor syntax to indicate the end of a TransLaTeX replacement block."""
    DEFAULT_REPLACEMENT_BLOCK_SEPERATOR: str = "%@--"
    """Default preprocessor syntax to indicate the separation of original LaTeX and replacement suggestion
    of a TransLaTeX replacement block."""
    ENABLE_SUBSTITUTION: bool = True
    DISABLE_SUBSTITUTION: bool = False

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

    def dump_store(self) -> str:
        string_transformed = [str(item) + "\n" for item in self._indicator_store.items()]
        return "".join(string_transformed)

    def process(self) -> None:
        r"""This operation makes the Preprocessor replace all manual substitution blocks with indicators.

        The replaced string gets saved into a dictionary to be used in rebuilding later. The whole block,
        meaning complete lines are taken into account. Any other text located after the "begin/end" statements on the
        same line as them aren't taken into account. This can be used by end users to personally annotate these blocks
        with custom text.

        Any number of dashes can follow the delimiter of the manual replacement block. This can be useful for
        end users to increase readability in their LaTeX files.

        And lastly, LaTeX comment delimiters are ignored during substitution. They are removed from the replacement
        suggestion. This can be helpful when you want to comment out these parts so that they don't affect the original
        work's rendering.

        For example:

        -> Before

        .. code-block:: latex

            %@{ This is my manual replacement block
            \textbf{Welcome to France!}
            %@-------------------------------------
            \textit{Bienvenue en France !}
            % $x < 3$
            %@} Here is the end of the block

        -> After substitution

        .. code-block:: latex

            %@=Manual intervention by TransLaTeX
            \textit{Bienvenue en France !}
            $x < 3$

        After the rebuild, the place where a manual substitution took place gets annotated by TransLaTeX for end users to
        locate them easier when proofreading.

        The resulting string is stored in an instance variable for processed LaTeX.
        """
        current_string = self._unprocessed_latex
        if not current_string:
            raise ValueError("Unprocessed string is empty, nothing to process")
        pattern = re.compile(re.escape(Preprocessor.DEFAULT_REPLACEMENT_BLOCK_BEGIN) + r"[\s\S]*" + re.escape(
            Preprocessor.DEFAULT_REPLACEMENT_BLOCK_SEPERATOR) + r"[\s\S]*" + re.escape(
            Preprocessor.DEFAULT_REPLACEMENT_BLOCK_END) + r".*")
        all_replaced = False
        while not all_replaced:
            match = pattern.search(current_string)
            if match:
                self._indicator_store.update({self.indicator_count + 1: match[0]})
                current_string, _ = pattern.subn(self._next_indicator(), current_string, 1)
            else:
                all_replaced = True
        self._processed_latex = current_string

    def rebuild(self, substitution_setting: bool = ENABLE_SUBSTITUTION) -> None:
        """Actual substitution is performed here during the rebuild. It can be disabled with the optional parameter
        indicating this setting.

        When disabled, the manual replacement blocks are reintroduced back into the string as is and no substitution
        occurs. Otherwise, by default, the second half of the block indicated by the delimiter is extracted, rid of
        any preceding LaTeX line comment or space characters and put where the corresponding indicator is standing in
        the string prepended with an annotation on a new line. See docstring for :py:meth:`process`.

        The resulting string is stored in an instance variable for unprocessed LaTeX.
        """
        current_string = self._processed_latex
        if not current_string:
            raise ValueError("Processed string is empty, nothing to rebuild")
        pattern = re.compile(re.escape(Preprocessor.DEFAULT_REPLACEMENT_BLOCK_SEPERATOR) + r".*\n([\s\S]*)\n\s*" +
                             re.escape(Preprocessor.DEFAULT_REPLACEMENT_BLOCK_END))
        pattern2 = re.compile(r"^(\s*)[%\s]*", re.MULTILINE)  # To filter out any line comment characters and spaces
        for indicator, value in self._indicator_store.items():
            replacement_string = value
            if substitution_setting:
                replacement_string = Preprocessor.DEFAULT_OPERATION_STAMP + "\n" + \
                                     pattern2.sub(r"\1", pattern.search(replacement_string)[1])
            formatted_indicator = self._indicator_format.format(indicator)
            if current_string.count(formatted_indicator) == 0:
                print("Missing or altered indicator: {} --> during stage PREPROCESSOR".format(formatted_indicator),
                      file=sys.stderr)
            else:
                current_string = current_string.replace(formatted_indicator, replacement_string)
        self._unprocessed_latex = current_string
