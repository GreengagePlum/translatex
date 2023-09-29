import pytest

from translatex.translator import TRANSLATION_SERVICE_CLASSES, Translator

TEST_SERVICE = TRANSLATION_SERVICE_CLASSES["DeepL"]
TEST_SERVICE_CLASSES = [
    TRANSLATION_SERVICE_CLASSES["Google Translate"],
    TRANSLATION_SERVICE_CLASSES["DeepL"],
]


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
