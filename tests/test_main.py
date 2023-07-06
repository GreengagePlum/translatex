import pathlib
from translatex.translator import Translator, TRANSLATION_SERVICES
from translatex.tokenizer import Tokenizer
from translatex.marker import Marker
from translatex.preprocessor import Preprocessor
from translatex.main import parse_args, translatex

TEXFILES_DIR_PATH = pathlib.Path(__file__).parent.resolve() / "texfiles"

TEST_SERVICE = TRANSLATION_SERVICES[1]


def translate(source: str, source_lang_code: str = 'en',
              destination_lang_code: str = 'fr') -> str:
    """
    Return a translated LaTeX string from source string
    in source lang to destination lang.
    """
    p = Preprocessor(source)
    p.process()
    m = Marker.from_preprocessor(p)
    m.mark()
    t = Tokenizer.from_marker(m)
    t.tokenize()
    a = Translator.from_tokenizer(t)
    a.translate(TEST_SERVICE, source_lang_code, destination_lang_code)
    t.update_from_translator(a)
    t.detokenize()
    m.update_from_tokenizer(t)
    m.unmark()
    p.update_from_marker(m)
    p.rebuild()
    return p.unprocessed_latex


def test_full_translation():
    source = r"""
\documentclass{article}
\begin{document}
Hello World
\end{document}
"""
    translated = translate(source)
    assert translated == r"""
\documentclass{article}
\begin{document}
Bonjour le monde
\end{document}
"""


def test_main():
    source_path = TEXFILES_DIR_PATH / "helloworld.tex"
    args = parse_args(['-sl', 'en', '-dl', 'fr',
                       source_path.as_posix()])
    translatex(args)
