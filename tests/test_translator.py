"""translator module test suite"""
from conftest import TEST_SERVICE
from textwrap import dedent


def test_split_string_by_length(trans):
    s = "Yes, 3.14 is an approximation of pi."
    assert trans.split_string_by_length(s, 100) == [s]
    assert trans.split_string_by_length(s, 4) == [s]

    s = "Hello world. I'm a 2-sentence string."
    assert trans.split_string_by_length(s, 100) == [s]
    assert trans.split_string_by_length(s, 4) == ["Hello world. ",
                                                  "I'm a 2-sentence string."]

    s = dedent("""
    Hello world.
    I'm a string.
    On multiple
    lines.
    """)
    chunks = trans.split_string_by_length(s, 4)
    assert chunks == ["\nHello world.\n", "I'm a string.\n",
                      "On multiple\nlines."]


def test_translate(trans):
    trans.translate(service=TEST_SERVICE)
    assert trans.translated_string == dedent("""
    [0-4]
    [0-3]{[0-1] Hello world}
    [0-2]
    [0-5]
    """)
