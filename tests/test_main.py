import pathlib
from conftest import TEST_SERVICE
from translatex.translator import Translator
from translatex.tokenizer import Tokenizer
from translatex.marker import Marker
from translatex.preprocessor import Preprocessor
from translatex.main import parse_args, translatex

TEXFILES_DIR_PATH = pathlib.Path(__file__).parent.resolve() / "texfiles"


def translate(source: str, source_lang_code: str = 'en',
              destination_lang_code: str = 'fr') -> str:
    """
    Return a translated LaTeX string from source string
    in source lang to destination lang.
    """
    p = Preprocessor(source)
    p.process()
    # print(f"Preprocessed LaTeX: {p._processed_latex}")
    m = Marker.from_preprocessor(p)
    m.mark()
    # print(f"Marked LaTeX: {m._marked_latex}")
    t = Tokenizer.from_marker(m)
    t.tokenize()
    # print(f"Tokenized LaTeX: {t._tokenized_string}")
    a = Translator.from_tokenizer(t)
    a.translate(TEST_SERVICE, source_lang_code, destination_lang_code)
    # print(f"Translated LaTeX: {a.translated_string}")
    t.update_from_translator(a)
    t.detokenize()
    # print(f"Detokenized LaTeX: {t._marked_string}")
    m.update_from_tokenizer(t)
    m.unmark()
    # print(f"Unmarked LaTeX: {m.unmarked_latex}")
    p.update_from_marker(m)
    p.rebuild()
    return p.unprocessed_latex


def test_full_translation():
    source = r"""\documentclass{article}
\begin{document}
Hello World
\end{document}
"""
    translated = translate(source)
    assert translated == r"""\documentclass{article}
\begin{document}
Bonjour le monde
\end{document}
"""


def test_translation_with_no_document_env():
    source = r"\section{Hello World}"
    translated = translate(source)
    assert translated == r"\section{Bonjour le monde}"


def test_main(tmp_path):
    source_file_path = TEXFILES_DIR_PATH / "helloworld.tex"
    destination_file_path = tmp_path / "helloworld_out.tex"
    args = parse_args(['-sl', 'en', '-dl', 'fr',
                       source_file_path.as_posix(),
                       destination_file_path.as_posix()])
    translatex(args)
    with open(destination_file_path, 'r') as f:
        translation_string = f.read()
        assert translation_string == r"""\documentclass{article}
\begin{document}
Bonjour le monde
\end{document}
"""
