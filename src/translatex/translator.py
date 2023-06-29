"""bla"""
from dataclasses import dataclass
import os
import re
import requests
import sys
from typing import List, Dict, Any

from googletrans import Translator as gTrans
import googletrans
from translatex.marker import Marker  # temporary
from translatex.preprocessor import Preprocessor  # temporary
from translatex.tokenizer import Tokenizer


@dataclass
class TranslationService:
    """An abstract class that represents a translation service."""
    name = str()
    overall_char_limit = int()
    char_limit = int()
    array_support = bool()
    array_item_limit = int()
    array_item_char_limit = int()
    array_overall_char_limit = int()
    url = str()
    languages = Dict[str, str]

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        """Return a translated string from source language to destination language."""
        return text


class GoogleTranslate(TranslationService):
    """Translate using Google API."""
    name = "Google Translate"
    overall_char_limit = 500000
    char_limit = 5000
    array_support = True
    array_item_limit = 1024
    array_item_char_limit = 0
    array_overall_char_limit = 30000
    url = 'https://translation.googleapis.com/language/translate/v2'
    languages = {code: lang.capitalize()
                 for code, lang in googletrans.LANGUAGES.items()}

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Return a translated string from source language to destination language."""
        try:
            google_api_key = os.environ['GOOGLE_API_KEY']
        except KeyError:
            exit(
                "Please set the environment variable GOOGLE_API_KEY to your Google API key.")
        headers = {'X-goog-api-key': google_api_key}
        payload = {'q': text,
                   'source': source_lang,
                   'target': target_lang,
                   'format': 'text'}
        print(payload)

        r = requests.post(self.url, headers=headers, data=payload)
        try:
            return r.json()['data']['translations'][0]['translatedText']
        except Exception as e:
            print(e)
            print(str(r))
            exit()


class IRMA(GoogleTranslate):
    name = "IRMA - M2M100"
    url = 'https://dlmds.math.unistra.fr/translation'

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        payload = {'text': text,
                   'source_lang': source_lang,
                   'target_lang': target_lang}
        r = requests.post(self.url, json=payload)
        try:
            return r.json()["translations"][0]["text"]
        except Exception as e:
            print(e)
            return str(r.json())


class GoogleTranslateNoKey(GoogleTranslate):
    """
    Use googletrans without an API key.
    This is not recommended, as it is against Google's TOS.
    """
    name = "Google Translate (no key)"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return gTrans().translate(text, src=source_lang, dest=target_lang).text


TRANSLATION_SERVICES: Dict[str, TranslationService | GoogleTranslate | IRMA] = {
    GoogleTranslate.name: GoogleTranslate(),
    GoogleTranslateNoKey.name: GoogleTranslateNoKey(),
    IRMA.name: IRMA()
}


class Translator:
    """Translator for tokenized LaTeX depending on the chosen languages and service.

    bla
    """
    DEFAULT_SOURCE_LANG: str = "fr"
    DEFAULT_DEST_LANG: str = "en"
    DEFAULT_SERVICE_NAME: str = GoogleTranslate.name

    def __init__(self, tokenized_string: str, token_format: str = Tokenizer.DEFAULT_TOKEN_FORMAT,
                 service_name=DEFAULT_SERVICE_NAME) -> None:
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
        self.service: dict = TRANSLATION_SERVICES[service_name]
        self._token_format: str = token_format

    @classmethod
    def from_tokenizer(cls, tokenizer: Tokenizer, service_name=DEFAULT_SERVICE_NAME) -> "Translator":
        """Another constructor that creates a Translator from a given Tokenizer. For convenience."""
        return cls(tokenizer.tokenized_string, tokenizer.token_format, service_name=service_name)

    def __str__(self) -> str:
        return "The translator has a base string of length {} characters.".format(len(self._base_string))

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
        if not self._token_format:
            raise ValueError("Tokenized string is empty, nothing to translate")
        latex_header, *tokenized_rest = re.split(r"(" + Tokenizer.token_regex(self._token_format) + r")",
                                                 self._tokenized_string, 1)
        if len(tokenized_rest) == 0:
            raise ValueError("No tokens found, translation halted")
        result_string = latex_header
        chunks = Translator.split_string_by_length(
            "".join(tokenized_rest), self.service["char-limit"])
        for chunk in chunks:
            result_string += self.service.translate(chunk,
                                                    src=self.source_lang,
                                                    dest=self.destination_lang)
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
