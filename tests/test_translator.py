"""translator module test suite"""
from textwrap import dedent

import pytest

from conftest import TEST_SERVICE_CLASSES
from translatex.translator import (TRANSLATION_SERVICE_CLASSES,
                                   add_custom_translation_services)


def test_split_string_by_length(small_trans):
    s = "Yes, 3.14 is an approximation of pi."
    assert small_trans.split_string_by_length(s, 100) == [s]
    assert small_trans.split_string_by_length(s, 4) == [s]

    s = "Hello world. I'm a 2-sentence string."
    assert small_trans.split_string_by_length(s, 100) == [s]
    assert small_trans.split_string_by_length(s, 4) == [
        "Hello world. ",
        "I'm a 2-sentence string."]

    s = dedent("""
    Hello world.
    I'm a string.
    On multiple
    lines.
    """)
    chunks = small_trans.split_string_by_length(s, 4)
    assert chunks == ["\nHello world.\n", "I'm a string.\n",
                      "On multiple\nlines."]


@pytest.mark.api
@pytest.mark.parametrize("service_class", TEST_SERVICE_CLASSES)
def test_translate_small(small_trans, service_class):
    small_trans.translate(service=service_class(),
                          source_lang="en",
                          destination_lang="fr")
    assert small_trans.translated_string == dedent("""
    [0-4]
    [0-3]{[0-1] Bonjour le monde}
    [0-2]
    [0-5]
    """)


@pytest.mark.api
@pytest.mark.parametrize("service_class", TEST_SERVICE_CLASSES)
def test_translate_math(math_trans, service_class):
    math_trans.translate(service=service_class())
    assert math_trans.translated_string == dedent("""
    [0-2]
    [0-1]
    [0-3]
    """)


def test_add_custom_translation_services(tmp_path):
    s = """\
from translatex.translator import TranslationService, GoogleTranslate

class TestService(TranslationService):
    name = "Test service"

    def translate(self, text):
        return "Always yes"

class TestService2(TranslationService):
    name = "Test service 2"

    def translate(self, text):
        return "Always no"

"""

    custom_file = tmp_path / 'custom.py'
    with open(custom_file, 'w') as f:
        f.write(s)

    with open(custom_file, 'r') as f:
        add_custom_translation_services(f)
    assert TRANSLATION_SERVICE_CLASSES["Test service"]().translate(
        "foo") == "Always yes"
    assert TRANSLATION_SERVICE_CLASSES["Test service 2"]().translate(
        "foo") == "Always no"
