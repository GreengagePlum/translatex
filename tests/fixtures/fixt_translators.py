import pytest
from translatex.translator import Translator, TRANSLATION_SERVICES


@pytest.fixture
def trans(small_tokenizer) -> Translator:
    tok = small_tokenizer
    tok.tokenize()
    return Translator.from_tokenizer(tok)


TEST_SERVICE = TRANSLATION_SERVICES[0]
