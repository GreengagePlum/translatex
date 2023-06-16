import regex as re
from typing import Dict

from translatex.marker import Marker

from translatex.data import *


class Tokenizer:
    DEFAULT_INITIAL_TOKEN_INDEX: int = 0
    DEFAULT_INITIAL_TOKEN_SUBINDEX: int = 0
    DEFAULT_TOKEN_SUBLIMIT: int = 16
    DEFAULT_TOKEN_FORMAT: str = "[{},{}]"
    DEFAULT_DETOKENIZER_CONTENT_INDICATOR: str = "%%"

    def __init__(self, marked_string: str, marker_format: str = Marker.DEFAULT_MARKER_FORMAT) -> None:
        self._base_string: str = marked_string
        self._marked_string: str = marked_string
        self._tokenized_string: str = str()
        self._token_count: int = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount: int = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_sublimit: int = Tokenizer.DEFAULT_TOKEN_SUBLIMIT
        self.token_format: str = Tokenizer.DEFAULT_TOKEN_FORMAT
        self._marker_format: str = marker_format
        self._token_store: Dict[str, str] = dict()

    def __str__(self) -> str:
        return "The tokenizer format is {} and tokenizer count is at {}.".format(self._token_format,
                                                                                 self.total_token_count())

    def total_token_count(self) -> int:
        return self._token_count * self._token_sublimit + self._token_subcount

    def _next_token(self) -> str:
        if self._token_subcount >= self._token_sublimit:
            self._token_subcount = 0
            self._token_count += 1
        else:
            self._token_subcount += 1
        return self.token_format.format(self._token_count, self._token_subcount)

    @property
    def marked_string(self) -> str:
        """This property contains currently marked string that was once correct LaTeX"""
        return self._marked_string

    @marked_string.setter
    def marked_string(self, marked_string: str) -> None:
        """If this property is set, tokenized string, and all tokenizer related stuff gets reset so that everything is
        in sync"""
        self._marked_string = marked_string
        self._tokenized_string = str()
        self._token_count = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_store = dict()

    @property
    def tokenized_string(self) -> str:
        """This property contains the tokenized, ready to translate string after tokenization operations."""
        return self._tokenized_string

    @tokenized_string.setter
    def tokenized_string(self, tokenized_string: str) -> None:
        """If this property is set, marked string gets reset so that everything is in sync"""
        self._tokenized_string = tokenized_string
        self._marked_string = str()

    @property
    def base_string(self) -> str:
        """The starting marked string. Saved aside so the original source is kept intact and accessible if need be."""
        return self._base_string

    @base_string.setter
    def base_string(self, base_string: str) -> None:
        """If the base changes, almost everything is reset and readied for the new base so that everything is in sync"""
        self._base_string = self._marked_string = base_string
        self._tokenized_string = str()
        self._token_count = Tokenizer.DEFAULT_INITIAL_TOKEN_INDEX
        self._token_subcount = Tokenizer.DEFAULT_INITIAL_TOKEN_SUBINDEX
        self._token_store = dict()

    @property
    def token_format(self) -> str:
        """The format string for tokens to be used."""
        return self._token_format

    @token_format.setter
    def token_format(self, format_str: str) -> None:
        """Set token format to be used.

        Args:
            format_str: A string that can be used with ``.format()``

        Raises:
            ValueError: If the given string doesn't have at least two occurrences of two empty curly braces "{}"

        """
        pattern = r'\{\}'
        matches = re.findall(pattern, format_str, re.DOTALL)
        if len(matches) < 2:
            raise ValueError("Not enough empty curly braces in the given format string")
        self._token_format = format_str

    def _token_regex(self) -> str:
        first_curly_start = self._token_format.find(r"{}")
        second_curly_start = self._token_format.find(r"{}", first_curly_start + 2)
        escaped_token_format = re.escape(self._token_format[:first_curly_start]) + "{}" + re.escape(
            self._token_format[first_curly_start + 2:second_curly_start]) + "{}" + re.escape(
            self._token_format[second_curly_start + 2:])
        return escaped_token_format.format(r"(?:\d+)", r"(?:\d+)")

    def _tokenize_completely_removed(self, process_string: str) -> str:
        current_string = process_string
        for e in COMPLETELY_REMOVED_COMMANDS:
            pattern = re.compile(r"\\" + e + r"(?:\[.*\])*(\{[^{}]+\})+(?:\[.*\])*")
            all_replaced = False
            while not all_replaced:
                next_token = self._next_token()
                match = pattern.search(current_string)
                if match:
                    self._token_store.update({next_token: match[0]})
                current_string, replace_count = pattern.subn(next_token, current_string, 1)
                if replace_count == 0:
                    all_replaced = True
        return current_string

    def _tokenize_specials(self, process_string: str) -> str:
        # TODO: Manage all special cases listed in data module
        current_string = process_string
        pattern = r"\\item"
        next_token = self._next_token()
        match = re.search(pattern, current_string)
        if match:
            self._token_store.update({next_token: match[0]})
        current_string = re.sub(pattern, next_token, current_string)
        return current_string

    def _tokenize_unnamed_math_optimized(self, process_string: str) -> str:
        marker_regex = self._marker_format.format(r"(?:\d+)")
        pattern = re.compile(r"(\\\[|\\\(|\$|\$\$)(?:" + marker_regex + r"\s*)*(\\\]|\\\)|\$|\$\$)?")
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            next_token = self._next_token()
            match = pattern.search(current_string)
            if match:
                self._token_store.update({next_token: match[0]})
            current_string, replace_count = pattern.subn(next_token, current_string, 1)
            if replace_count == 0:
                all_replaced = True
        pattern = re.compile(r"(?:" + marker_regex + r")*(\\\]|\\\)|\$|\$\$)")
        all_replaced = False
        while not all_replaced:
            next_token = self._next_token()
            match = pattern.search(current_string)
            if match:
                self._token_store.update({next_token: match[0]})
            current_string, replace_count = pattern.subn(next_token, current_string, 1)
            if replace_count == 0:
                all_replaced = True
        return current_string

    def _tokenize_commands(self, process_string: str) -> str:
        # TODO: Conflicts with token format when matching all square brackets "[]", correct behaviour if necessary
        marker_regex = self._marker_format.format(r"(?:\d+)")
        # pattern = re.compile(r"\\" + marker_regex + r"(?:\[.*\])*(?:(?:(?:\{[^{}]+\})*(\{.*\}))|(\{.*\})?)(?:\[.*\])*")
        # pattern = re.compile(r"\\" + marker_regex + r"(?:\[.*\])*(?:(?:(?:\{[^{}]+\})*(\{(?:(?:[^{}]|(?<=(?<!\\)(?:\\\\)*(?:\\{2})*\\){[^{}]*})+|(?R))+\}))|(\{.*\})?)(?:\[.*\])*")
        pattern = re.compile(r"\\" + marker_regex + r"(?:\[.*\])*(?:(?:(?:\{[^{}]+\})*(\{(?:(?:[^{}]|(?<=(?<!\\)(?:\\\\)*(?:\\{2})*\\){[^{}]*})+|(?R))*\}))|(\{.*\})?)(?:\[.*\])*")
        # pattern = re.compile(r"\\" + marker_regex + r"(?:\[.*\])*(?:(?:(?:\{[^{}]+\})*(\{(?:(?:[^{}]|(?<=(?<!\\)(?:\\\\)*(?:\\{2})*\\){[^{}]*})+)+\}))|(\{.*\})?)(?:\[.*\])*")
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            next_token = self._next_token()
            match = pattern.search(current_string)
            if match:
                if match[1]:
                    stored_string = match[0][:match.start(1) - match.start(
                        0)] + Tokenizer.DEFAULT_DETOKENIZER_CONTENT_INDICATOR + match[0][match.end(1) - match.start(0):]
                    self._token_store.update({next_token: stored_string})
                else:
                    self._token_store.update({next_token: match[0]})
            current_string, replace_count = pattern.subn(next_token + r"\1", current_string, 1)
            if replace_count == 0:
                all_replaced = True
        return current_string

    def _tokenize_named_envs(self, process_string: str) -> str:
        marker_regex = self._marker_format.format(r"(?:\d+)")
        pattern = re.compile(
            r"\\begin\{" + marker_regex + r"\}(\[.*\])*(?:\s*" + marker_regex + r"\s*)*(?:\\end\{" + marker_regex + r"\})?")
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            next_token = self._next_token()
            match = pattern.search(current_string)
            if match:
                self._token_store.update({next_token: match[0]})
            current_string, replace_count = pattern.subn(next_token, current_string, 1)
            if replace_count == 0:
                all_replaced = True
        pattern = re.compile(
            r"(?:\s*[^\\]" + marker_regex + r")*(?:\\end\{" + marker_regex + r"\})")
        all_replaced = False
        while not all_replaced:
            next_token = self._next_token()
            match = pattern.search(current_string)
            if match:
                self._token_store.update({next_token: match[0]})
            current_string, replace_count = pattern.subn(next_token, current_string, 1)
            if replace_count == 0:
                all_replaced = True
        return current_string

    def _tokenize_markers(self, process_string: str) -> str:
        marker_regex = self._marker_format.format(r"(?:\d+)")
        pattern = re.compile(marker_regex)
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            next_token = self._next_token()
            match = pattern.search(current_string)
            if match:
                self._token_store.update({next_token: match[0]})
            current_string, replace_count = pattern.subn(next_token, current_string, 1)
            if replace_count == 0:
                all_replaced = True
        return current_string

    def _tokenize_comments(self, process_string: str) -> str:
        pattern = re.compile(r"(?<!\\)(?:\\\\)*%.*$", re.MULTILINE)
        current_string = process_string
        all_replaced = False
        while not all_replaced:
            next_token = self._next_token()
            match = pattern.search(current_string)
            if match:
                self._token_store.update({next_token: match[0]})
            current_string, replace_count = pattern.subn(next_token, current_string, 1)
            if replace_count == 0:
                all_replaced = True
        return current_string

    def _tokenize_latex_spacers(self, process_string: str) -> str:
        current_string = process_string
        for e in LATEX_SPACERS:
            pattern = re.escape(e)
            next_token = self._next_token()
            match = re.search(pattern, current_string)
            if match:
                self._token_store.update({next_token: match[0]})
            current_string = re.sub(pattern, next_token, current_string)
        return current_string

    def tokenize(self):
        # TODO: Make marker regex dynamic in the line below since it can be variable
        split_strings: List[str] = re.split(r"(^.*//(?:\d+)//.*$)", self._marked_string, 1, re.MULTILINE)
        header_string: str = split_strings[0]
        main_string: str = split_strings[1] + split_strings[2]
        main_string = self._tokenize_completely_removed(main_string)
        main_string = self._tokenize_specials(main_string)
        main_string = self._tokenize_unnamed_math_optimized(main_string)
        main_string = self._tokenize_commands(main_string)
        main_string = self._tokenize_named_envs(main_string)
        main_string = self._tokenize_markers(main_string)
        main_string = self._tokenize_comments(main_string)
        main_string = self._tokenize_latex_spacers(main_string)
        self._tokenized_string = header_string + main_string

    def detokenize(self):
        main_string: str = self._tokenized_string
        # TODO: The following for loop for checking errors might need a change (tokens might be tokenized and not
        #  directly visible during a first iteration)
        # for token in self._token_store.keys():
        #     if main_string.find(token) == -1:
        #         raise LookupError("Detected missing token in string to detokenize")
        token_regex = self._token_regex()
        # pattern = re.compile(r"(" + token_regex + r")(\{(?:(?<!\\)(?:\\\\)*[^{}]+|(?R))+\})")
        pattern = re.compile(
            r"(" + token_regex + r")(\{(?:(?:[^{}]|(?<=(?<!\\)(?:\\\\)*(?:\\{2})*\\){[^{}]*})+|(?R))+\})")
        all_commands_replaced = False
        while not all_commands_replaced:
            match = pattern.search(main_string)
            if match:
                replace_string = self._token_store[match[1]].replace(Tokenizer.DEFAULT_DETOKENIZER_CONTENT_INDICATOR,
                                                                     match[2], 1)
                main_string = pattern.sub(replace_string, main_string, 1)
            else:
                all_commands_replaced = True
        for token, value in self._token_store.items():
            main_string = main_string.replace(token, value)
        self._marked_string = main_string


if __name__ == "__main__":
    base_file = "translatex"
    with open(f"../../examples/{base_file}.tex") as f:
        m = Marker(f.read())

    m.mark()
    with open(f"../../examples/{base_file}_post.tex", "w+") as f:
        f.write(m.marked_latex)

    t = Tokenizer(m.marked_latex)
    t.tokenize()
    print("wow")
    t.detokenize()
    with open(f"../../examples/{base_file}_post2.tex", "w+") as f:
        # f.write(t.tokenized_string)
        f.write(t.marked_string)
