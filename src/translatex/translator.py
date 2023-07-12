"""The translation module is where all the logic for the last stage of TransLaTeX resides.

Abstractions for different translation services and APIs as well as methods to resize strings to optimize the number of
API calls.
"""
import logging
import os
import re
from typing import Dict

import requests
import googletrans

from .tokenizer import Tokenizer

log = logging.getLogger(__name__)


class TranslationService:
    """An abstract class that represents a translation service."""
    name: str = str()
    overall_char_limit: int = int()
    char_limit: int = int()
    array_support: bool = bool()
    array_item_limit: int = int()
    array_item_char_limit: int = int()
    array_overall_char_limit: int = int()
    url: str = str()
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

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        """Return a translated string from source language to destination language."""
        try:
            google_api_key = os.environ['GOOGLE_API_KEY']
        except KeyError:
            error_message = "Please set the environment variable GOOGLE_API_KEY to your Google API key."
            log.error(error_message)
            # Return a LaTeX comment with the error message
            return f"% {error_message}"
        headers = {'X-goog-api-key': google_api_key}
        payload = {'q': text,
                   'source': source_lang,
                   'target': dest_lang,
                   'format': 'text'}

        r = requests.post(self.url, headers=headers, data=payload)
        try:
            return r.json()['data']['translations'][0]['translatedText']
        except Exception as e:
            log.error(e)
            log.error(str(r))
            return str(r)


class IRMA(GoogleTranslate):
    """Translate using Unistra IRMA DLMDS."""
    name = "IRMA - M2M100"
    char_limit = 1000
    url = 'https://dlmds.math.unistra.fr/translation'

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        payload = {'text': text,
                   'source_lang': source_lang,
                   'target_lang': dest_lang}
        r = requests.post(self.url, json=payload)
        try:
            return r.json()["translations"][0]["text"]
        except Exception as e:
            log.error(e)
            return str(r.json())


class GoogleTranslateNoKey(GoogleTranslate):
    """Use googletrans without an API key.

    This is not recommended, as it is against Google's TOS.
    """
    name = "Google Translate (no key)"

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        return googletrans.Translator().translate(text, src=source_lang, dest=dest_lang).text


TRANSLATION_SERVICES = (GoogleTranslate(),
                        GoogleTranslateNoKey(),
                        IRMA())
if os.environ.get("GOOGLE_API_KEY") is None:
    TRANSLATION_SERVICES = TRANSLATION_SERVICES[1:]
TRANSLATION_SERVICES_BY_NAME = {service.name: service
                                for service in TRANSLATION_SERVICES}


class Translator:
    """Translator for tokenized LaTeX depending on the chosen languages and service.

    Splits the source string into reasonable chunks using a full stop as a seperator while trying to approach the used
    service's limit per request as closely as possible to make the least number of API calls.

    The operation is one way only. Once an instance is created, the tokenized source string is translated to the given
    language in the related instance variable. You can change the source string and languages and launch another
    translation.
    """
    DEFAULT_SOURCE_LANG: str = "fr"
    DEFAULT_DEST_LANG: str = "en"
    DEFAULT_SERVICE = TRANSLATION_SERVICES[1]

    def __init__(self, tokenized_string: str, token_format: str = Tokenizer.DEFAULT_TOKEN_FORMAT) -> None:
        """Creates a Tokenizer with default settings.

        Default settings are taken from the class variables.

        Args:
            tokenized_string: The string that contains tokenized LaTeX
            token_format: The format string used for tokens
            service_name: Name of the translation service to use

        """
        self._base_string: str = tokenized_string
        self._tokenized_string: str = tokenized_string
        self._translated_string: str = str()
        self._token_format: str = token_format

    @classmethod
    def from_tokenizer(cls, tokenizer: Tokenizer) -> "Translator":
        """Another constructor that creates a Translator from a given Tokenizer. For convenience."""
        return cls(tokenizer.tokenized_string, tokenizer.token_format)

    def __str__(self) -> str:
        return f"The translator has a base string of length {len(self._base_string)} characters."

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

    def translate(self,
                  service=DEFAULT_SERVICE,
                  source_lang: str = DEFAULT_SOURCE_LANG,
                  destination_lang: str = DEFAULT_DEST_LANG) -> None:
        """Translation is performed with the set source and destination languages and the chosen service.

        The Result is stored in an instance variable.

        Raises:
            ValueError: If the source string is empty
            ValueError: If the source string contains no tokens

        """
        if not self._token_format:
            raise ValueError("Tokenized string is empty, nothing to translate")
        latex_header, *tokenized_rest = re.split(r"(" + Tokenizer.token_regex(self._token_format) + r")",
                                                 self._tokenized_string, 1)
        if len(tokenized_rest) == 0:
            raise ValueError("No tokens found, translation halted")
        result_string = latex_header
        chunks = Translator.split_string_by_length(
            "".join(tokenized_rest), service.char_limit)
        for chunk in chunks:
            result_string += service.translate(chunk,
                                               source_lang=source_lang,
                                               dest_lang=destination_lang)
        self._translated_string = result_string
