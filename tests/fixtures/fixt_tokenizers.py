import pytest
from translatex.tokenizer import Tokenizer


@pytest.fixture
def small_tokenizer(small_marker) -> Tokenizer:
    m = small_marker
    m.mark()
    return Tokenizer.from_marker(m)


@pytest.fixture
def math_tokenizer(math_marker) -> Tokenizer:
    m = math_marker
    m.mark()
    return Tokenizer.from_marker(m)
