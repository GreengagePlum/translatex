from translatex.translator import Translator, TRANSLATION_SERVICES

TEST_SERVICE = TRANSLATION_SERVICES[1]


def test_translate(small_tokenizer):
    tok = small_tokenizer
    tok.tokenize()
    trans = Translator.from_tokenizer(tok)
    trans.translate(service=TEST_SERVICE)
    print(trans.translated_string)
    assert trans.translated_string == """
    [0.4]
    [0.3] {[0.1] Hello World}
    [0.2]
    [0.5]"""
