"""
The translation module is where all the logic for the last stage of TransLaTeX
resides.

Abstractions for different translation services and APIs as well as methods to
resize strings to optimize the number of API calls.
"""
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, TextIO

import deepl
import googletrans
import nltk
import requests
from nltk.tokenize import punkt

from .tokenizer import Tokenizer

log = logging.getLogger("translatex.translator")

# Download the Punkt tokenizer for sentence splitting
nltk.download("punkt", quiet=True)


class CustomLanguageVars(punkt.PunktLanguageVars):
    """
    A custom language vars class for the NLTK Punkt tokenizer that allows for
    sentence splitting preserving new lines.
    Taken from https://stackoverflow.com/a/33153483/5072688
    """

    _period_context_fmt = r"""
        \S*                          # some word material
        %(SentEndChars)s             # a potential sentence ending
        \s*                       #  <-- THIS is what I changed
        (?=(?P<after_tok>
            %(NonWord)s              # either other punctuation
            |
            (?P<next_tok>\S+)     #  <-- Normally you would have \s+ here
        ))"""


custom_tknzr = punkt.PunktSentenceTokenizer(lang_vars=CustomLanguageVars())


class ApiKeyError(Exception):
    """
    Raised when an API key is missing.

    Attributes:
        service_name: The name of the service that is missing an API key.
        env_variable_name: The name of the environment variable that is missing.
    """

    def __init__(self, service_name: str, env_variable_name: str) -> None:
        self.service_name = service_name
        self.env_variable_name = env_variable_name
        self.message = f"""\
{self.env_variable_name} environment variable is not set so {self.service_name} is \
not available.
Please set the {self.env_variable_name} environment variable to your \
{self.service_name} API key.
"""

        super().__init__(self.message)


class TranslationService(ABC):
    """An abstract class that represents a translation service.

    Attributes:
        name: Human friendly name for the service.
        overall_char_limit: The overall quota a user has on a service.
        char_limit: The maximum number of characters for the text body for a single API call (no array).
        array_support: If an API supports using arrays of strings in the call body.
        array_item_limit: How large an array of strings can be in terms of number of strings.
        array_item_char_limit: Maximum number of characters an array item can hold.
        array_overall_char_limit: Maximum number of characters an array can hold including all its items.
        url: The url to send requests to, the API endpoint.
        doc_url: Where to find the docs for the service.
        short_description: Short explanation for the service.
        languages: The languages supported by the service. Associates shortened ISO versions of languages to their
            official long versions.

    """

    name: str = str()
    overall_char_limit: int = int()
    char_limit: int = int()
    array_support: bool = bool()
    array_item_limit: int = int()
    array_item_char_limit: int = int()
    array_overall_char_limit: int = int()
    url: str = str()
    doc_url: str = str()
    short_description = str()
    languages = Dict[str, str]

    @abstractmethod
    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        """
        Return a translated string from source language to destination
        language.
        """
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
    url = "https://translation.googleapis.com/language/translate/v2"
    doc_url = "https://cloud.google.com/translate/docs/"
    short_description = "Google's translation service using an API key"
    languages = {
        code: lang.capitalize() for code, lang in googletrans.LANGUAGES.items()
    }

    def __init__(self):
        try:
            self.google_api_key = os.environ["GOOGLE_API_KEY"]
        except KeyError:
            raise ApiKeyError(self.name, "GOOGLE_API_KEY")

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        """
        Return a translated string from source language to destination
        language.
        """

        headers = {"X-goog-api-key": self.google_api_key}
        payload = {
            "q": text,
            "source": source_lang,
            "target": dest_lang,
            "format": "text",
        }
        log.debug("payload = %s", payload)
        r = requests.post(self.url, headers=headers, data=payload, timeout=10)
        try:
            return r.json()["data"]["translations"][0]["translatedText"]
        except Exception as e:
            log.error(e)
            log.error(str(r))
            log.error(r.json())
            return text


class GoogleTranslateNoKey(TranslationService):
    """Use googletrans without an API key.

    This is not recommended, as it is against Google's TOS.
    """

    name = "Google Translate (no key)"
    overall_char_limit = 500000
    char_limit = 5000
    array_support = True
    array_item_limit = 1024
    array_item_char_limit = 0
    array_overall_char_limit = 30000
    url = ""
    doc_url = "https://github.com/ssut/py-googletrans"
    short_description = (
        "Google's translation service without an API key "
        "(for testing purposes only)."
    )
    languages = {
        code: lang.capitalize() for code, lang in googletrans.LANGUAGES.items()
    }

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        return (
            googletrans.Translator()
            .translate(text, src=source_lang, dest=dest_lang)
            .text
        )


class DeepL(TranslationService):
    """Translate using DeepL API."""

    name: str = "DeepL"
    char_limit = 1024
    array_support = True
    array_item_limit = 50
    array_item_char_limit = 1024
    array_overall_char_limit = 1024
    doc_url = "https://www.deepl.com/docs-api"
    short_description = "DeepL translation service using an API key"

    def __init__(self):
        """
        Initialize the DeepL translator.
        """
        try:
            deepl_auth_key = os.environ["DEEPL_AUTH_KEY"]
        except KeyError:
            raise ApiKeyError(self.name, "DEEPL_AUTH_KEY")

        self.translator = deepl.Translator(deepl_auth_key)
        char_usage = self.translator.get_usage().character
        if char_usage.valid:
            self.overall_char_limit = char_usage.limit - char_usage.count
        language_list = self.translator.get_source_languages()
        self.languages = {
            language.code: language.name for language in language_list
        }

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        """
        Return a translated string from source language to destination
        language.
        """
        # "EN" is deprecated with DeepL, use "EN-GB" instead
        if dest_lang == "en":
            log.warning(
                "DeepL does not support 'en' as a destination language, "
                "using 'EN-GB' instead"
            )
            dest_lang = "EN-GB"
        # Language shortcodes for DeepL are in uppercase,
        # so we convert them in case they are lowercase
        result = self.translator.translate_text(
            text,
            source_lang=source_lang.upper(),
            target_lang=dest_lang.upper(),
        )
        return result.text


TRANSLATION_SERVICE_CLASSES = {
    cls.name: cls for cls in (GoogleTranslate, GoogleTranslateNoKey, DeepL)
}


class Translator:
    """
    Translator for tokenized LaTeX depending on the chosen languages and
    service.

    Splits the source string into reasonable chunks using a full stop as
    a seperator while trying to approach the used service's limit per request
    as closely as possible to make the least number of API calls.

    The operation is one way only. Once an instance is created, the tokenized
    source string is translated to the given language in the related instance
    variable. You can change the source string and languages and launch another
    translation.
    """

    DEFAULT_SERVICE: TranslationService = TRANSLATION_SERVICE_CLASSES[
        "Google Translate (no key)"
    ]()
    DEFAULT_SOURCE_LANG: str = "fr"
    DEFAULT_DEST_LANG: str = "en"

    def __init__(
        self,
        tokenized_string: str,
        token_format: str = Tokenizer.DEFAULT_TOKEN_FORMAT,
    ) -> None:
        """Creates a Tokenizer with default settings.

        Default settings are taken from the class variables.

        Args:
            tokenized_string: The string that contains tokenized LaTeX
            token_format: The format string used for tokens

        """
        self._base_string: str = tokenized_string
        self._tokenized_string: str = tokenized_string
        self._translated_string: str = str()
        self._token_format: str = token_format

    @classmethod
    def from_tokenizer(cls, tokenizer: Tokenizer) -> "Translator":
        """
        Another constructor that creates a Translator from a given
        Tokenizer. For convenience.
        """
        return cls(tokenizer.tokenized_string, tokenizer.token_format)

    def __str__(self) -> str:
        return (
            f"The translator has a base string of length "
            f"{len(self._base_string)} characters."
        )

    @property
    def tokenized_string(self) -> str:
        """
        This property contains currently tokenized string that was once
        correct LaTeX.

        If this property is set, translated string, and all translator-related
        stuff gets reset so that everything is in sync.
        """
        return self._tokenized_string

    @tokenized_string.setter
    def tokenized_string(self, tokenized_string: str) -> None:
        self._tokenized_string = tokenized_string
        self._translated_string = str()

    @property
    def translated_string(self) -> str:
        """
        This property contains the translated, ready to rebuild string
        after translation operations.

        If this property is set, tokenized string gets reset so that
        everything is in sync.
        """
        return self._translated_string

    @translated_string.setter
    def translated_string(self, translated_string: str) -> None:
        self._translated_string = translated_string
        self._tokenized_string = str()

    @property
    def base_string(self) -> str:
        """
        The starting tokenized string. Saved aside so the original source
        is kept intact and accessible if need be.

        If the base changes, almost everything is reset and readied for the
        new base so that everything is in sync.
        """
        return self._base_string

    @base_string.setter
    def base_string(self, base_string: str) -> None:
        self._base_string = self._tokenized_string = base_string
        self._translated_string = str()

    @staticmethod
    def split_string_by_length(string: str, max_length: int) -> List[str]:
        """
        Splits a string into chunks of sentences of a given maximum length.
        Preserves carriage returns and newlines.
        """

        chunks = []
        current_chunk = ""
        sentences = custom_tknzr.tokenize(string)

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def translate(
        self,
        service: TranslationService = DEFAULT_SERVICE,
        source_lang: str = DEFAULT_SOURCE_LANG,
        destination_lang: str = DEFAULT_DEST_LANG,
    ) -> None:
        """
        Translation is performed with the set source and destination
        languages and the chosen service.

        The Result is stored in an instance variable.

        Args:
            service: The translation service instance to use
            source_lang: The original language of the given string in ISO short form
            destination_lang: The target language to translate to in ISO short form

        Raises:
            ValueError: If the source string is empty

        """
        if not self._tokenized_string:
            raise ValueError("Tokenized string is empty, nothing to translate")
        latex_header, *tokenized_rest = re.split(
            f"({Tokenizer.token_regex(self._token_format)})",
            self._tokenized_string,
            1,
        )
        if len(tokenized_rest) == 0:
            # The case where there are no tokens: standard translation
            tokenized_rest = self._tokenized_string
            self._translated_string = ""
        else:
            self._translated_string = latex_header
        chunks = Translator.split_string_by_length(
            "".join(tokenized_rest), service.char_limit
        )
        self._translated_string += "".join(
            service.translate(
                chunk, source_lang=source_lang, dest_lang=destination_lang
            )
            for chunk in chunks
        )
        # For multiline strings, add a newline at the end if it was lost
        # during the process
        if (
            self._tokenized_string[-1] == "\n"
            and self._translated_string[-1] != "\n"
        ):
            self._translated_string += "\n"


def add_custom_translation_services(fp: TextIO):
    """
    Add to TRANSLATION_SERVICE_CLASSES the subclasses of TranslationService
    that are defined in the custom file fp.

    Args:
        fp: Input file object.
    """
    namespace: Dict[str, Any] = {}
    exec(compile(fp.read(), fp.name, "exec"), namespace)
    for obj in namespace.values():
        # Add the classes that are :
        #   - defined only in the file and not in the current module namespace
        #   - subclasses of TranslationService
        if (
            type(obj) is type(TranslationService)
            and obj.__name__ not in globals()
            and issubclass(obj, TranslationService)
        ):
            TRANSLATION_SERVICE_CLASSES[obj.name] = obj
