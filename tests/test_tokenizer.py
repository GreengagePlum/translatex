"""tokenizer module test suite"""
import pytest
import re

from translatex.tokenizer import Tokenizer


def test_creation(small_tokenizer):
    """Ensure Tokenizer created correctly with all its properties."""
    t = small_tokenizer
    assert t.base_string
    assert t.marked_string
    assert not t.tokenized_string


def test_token_count(small_tokenizer):
    """Verify number of tokens generated for a simple LaTeX snippet."""
    t = small_tokenizer
    t.tokenize()
    assert t.total_token_count() == 4


def test_modification1(small_tokenizer):
    """Ensure Tokenizer updates correctly when modified"""
    t = small_tokenizer
    base_before = t.base_string
    t.tokenized_string = "spam"
    assert t.base_string == base_before
    assert not t.marked_string
    assert t.tokenized_string


def test_modification2(small_tokenizer):
    """Ensure Tokenizer updates correctly when modified"""
    t = small_tokenizer
    base_before = t.base_string
    t.unmarked_latex = "spam"
    assert t.base_string == base_before
    assert t.marked_string
    assert not t.tokenized_string
    assert len(t._token_store) == 0
    assert t.total_token_count() == 0


def test_modification3(small_tokenizer):
    """Ensure Tokenizer updates correctly when modified"""
    mod_value = "spam"
    t = small_tokenizer
    t.base_string = mod_value
    assert t.base_string
    assert t.marked_string == mod_value
    assert not t.tokenized_string
    assert len(t._token_store) == 0
    assert t.total_token_count() == 0


def test_token_format(small_tokenizer):
    """Ensure token format setter works correctly"""
    t = small_tokenizer
    assert t.token_format == Tokenizer.DEFAULT_TOKEN_FORMAT
    try:
        t.token_format = "{}spam[]{}"
    except ValueError:
        pytest.fail()
    with pytest.raises(ValueError):
        t.token_format = "[]{eggs"


def test_token_regex(small_tokenizer):
    """Ensure Tokenizer correctly builds regex corresponding to its token format."""
    t = small_tokenizer
    t.token_format = "[{}.{}]"
    assert t._token_regex() == r"\[(?:\d+)\.(?:\d+)\]"


def test_undo_tokenization(small_tokenizer):
    """Ensure Tokenizer preserves all details of the original string when detokenization operation is done"""
    t = small_tokenizer
    t.tokenize()
    t.detokenize()
    assert t.base_string == t.marked_string


def test_empty_tokenization(small_tokenizer):
    """Ensure Tokenizer raises an error when trying to tokenize an empty string"""
    t = small_tokenizer
    t.marked_string = ""
    with pytest.raises(ValueError):
        t.tokenize()


def test_empty_detokenization(small_tokenizer):
    """Ensure Tokenizer raises an error when trying to detokenize an empty string"""
    t = small_tokenizer
    with pytest.raises(ValueError):
        t.detokenize()


def test_warning_detokenization(small_tokenizer, capsys):
    """Ensure Tokenizer warns about missing or altered tokens on ``stderr``"""
    t = small_tokenizer
    t.tokenize()
    t.detokenize()
    _, captured = capsys.readouterr()
    assert len(captured) == 0
    t.tokenized_string = "foo"
    t.detokenize()
    _, captured = capsys.readouterr()
    assert len(captured) > 0
