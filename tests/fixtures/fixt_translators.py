import pytest
from translatex.translator import Translator, TRANSLATION_SERVICES

TEST_SERVICE = TRANSLATION_SERVICES[0]


@pytest.fixture
def small_trans(small_tokenizer) -> Translator:
    tok = small_tokenizer
    tok.tokenize()
    return Translator.from_tokenizer(tok)


@pytest.fixture
def math_trans(math_tokenizer) -> Translator:
    tok = math_tokenizer
    tok.tokenize()
    return Translator.from_tokenizer(tok)
