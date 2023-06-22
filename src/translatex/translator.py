"""bla"""
import re
import sys
from typing import List, Dict, Any

from googletrans import Translator as gTrans
from translatex.marker import Marker  # temporary
from translatex.preprocessor import Preprocessor  # temporary
from translatex.tokenizer import Tokenizer

TRANSLATION_SERVICES: List[Dict[str, str | Dict[str, Any]]] = [
    {"name": "Google Translate",
     "properties": {"overall-char-limit": 500000,
                    "char-limit": 5000,
                    "array-support": True,
                    "array-item-limit": 1024,
                    "array-item-char-limit": 0,
                    "array-overall-char-limit": 30000,
                    "url": "https://translate.googleapis.com/v3/{parent=projects/*/locations/*}:translateText"}
     }, "DeepL", "TextSynth", "DLMDS", "Microsoft"]


class Translator:
    """Translator for tokenized LaTeX depending on the chosen languages and service.

    bla
    """
    DEFAULT_SOURCE_LANG: str = "fr"
    DEFAULT_DEST_LANG: str = "en"
    DEFAULT_SERVICE: dict = TRANSLATION_SERVICES[0]

    def __init__(self, tokenized_string: str, token_format: str = Tokenizer.DEFAULT_TOKEN_FORMAT) -> None:
        """Creates a Tokenizer with default settings.

        bla

        Args:
            tokenized_string: The string that contains tokenized LaTeX

        """
        self._base_string: str = tokenized_string
        self._tokenized_string: str = tokenized_string
        self._translated_string: str = str()
        self.source_lang = Translator.DEFAULT_SOURCE_LANG
        self.destination_lang = Translator.DEFAULT_DEST_LANG
        self.service: dict = Translator.DEFAULT_SERVICE
        self._token_format: str = token_format

    @classmethod
    def from_tokenizer(cls, tokenizer: Tokenizer) -> "Translator":
        """Another constructor that creates a Translator from a given Tokenizer. For convenience."""
        return cls(tokenizer.tokenized_string, tokenizer.token_format)

    def __str__(self) -> str:
        return "The translator has a base string of length {}".format(len(self._base_string))

    @property
    def tokenized_string(self) -> str:
        """This property contains currently tokenized string that was once correct LaTeX.

        If this property is set, translated string, and all translator-related stuff gets reset so that everything is
        in sync.
        """
        return self._tokenized_string

    @tokenized_string.setter
    def tokenized_string(self, tokenized_string: str) -> None:
        self._tokenized_string = tokenized_string
        self._translated_string = str()

    @property
    def translated_string(self) -> str:
        """This property contains the translated, ready to rebuild string after translation operations.

        If this property is set, tokenized string gets reset so that everything is in sync.
        """
        return self._translated_string

    @translated_string.setter
    def translated_string(self, translated_string: str) -> None:
        self._translated_string = translated_string
        self._tokenized_string = str()

    @property
    def base_string(self) -> str:
        """The starting tokenized string. Saved aside so the original source is kept intact and accessible if need be.

        If the base changes, almost everything is reset and readied for the new base so that everything is in sync
        """
        return self._base_string

    @base_string.setter
    def base_string(self, base_string: str) -> None:
        self._base_string = self._tokenized_string = base_string
        self._translated_string = str()

    @staticmethod
    def split_string_by_length(string, max_length):
        chunks = []
        current_chunk = ""
        for sentence in re.split(r"\.(?!\d+)", string):
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + '.'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '.'
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def translate(self) -> None:
        automatic_translator = gTrans()
        latex_header, *tokenized_rest = re.split(r"(" + Tokenizer.token_regex(self._token_format) + r")",
                                                 self._tokenized_string, 1)
        result_string = latex_header
        chunks = Translator.split_string_by_length("".join(tokenized_rest), self.service["properties"]["char-limit"])
        for chunk in chunks:
            result_string = result_string + automatic_translator.translate(chunk,
                                                                           src=self.source_lang,
                                                                           dest=self.destination_lang).text
        self._translated_string = result_string


if __name__ == "__main__":
    base_file = "translatex"
    with open(f"../../examples/{base_file}.tex") as f:
        p = Preprocessor(f.read())

    p.process()
    m = Marker.from_preprocessor(p)
    m.mark()
    t = Tokenizer.from_marker(m)
    t.tokenize()

    with open(f"../../examples/{base_file}_post.tex", "w+") as f:
        f.write(t.tokenized_string)

    a = Translator.from_tokenizer(t)
    a.translate()

    with open(f"../../examples/{base_file}_post2.tex", "w+") as f:
        f.write(a.translated_string)

    t.update_from_translator(a)
    t.detokenize()
    m.update_from_tokenizer(t)
    m.unmark()
    p.update_from_marker(m)
    p.rebuild()
    with open(f"../../examples/{base_file}_post3.tex", "w+") as f:
        f.write(p.unprocessed_latex)
