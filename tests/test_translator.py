"""translator module test suite"""
from textwrap import dedent

import pytest

from conftest import TEST_SERVICE


def test_split_string_by_length(small_trans):
    s = "Yes, 3.14 is an approximation of pi."
    assert small_trans.split_string_by_length(s, 100) == [s]
    assert small_trans.split_string_by_length(s, 4) == [s]

    s = "Hello world. I'm a 2-sentence string."
    assert small_trans.split_string_by_length(s, 100) == [s]
    assert small_trans.split_string_by_length(s, 4) == ["Hello world. ",
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
def test_translate_small(small_trans):
    small_trans.translate(service=TEST_SERVICE)
    assert small_trans.translated_string == dedent("""
    [0-4]
    [0-3]{[0-1] Hello world}
    [0-2]
    [0-5]
    """)


@pytest.mark.api
def test_translate_math(math_trans):
    math_trans.translate(service=TEST_SERVICE)
    assert math_trans.translated_string == dedent("""
    [0-2]
    [0-1]
    [0-3]
    """)
