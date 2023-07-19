"""TransLaTeX is a program which aims to translate LaTeX source files (``.tex``) from one human language to
another using automatic translators.

The purpose is to extract the text from LaTeX source files using a tokenization technique without including any commands
or tags so that the result can be passed to an automatic translator like DeepL or Google Translate without messing up
the LaTeX file. The objective is to have the same LaTeX file with only the text in another specified language which
still compiles perfectly and visually intact. A single, simple tool to translate LaTeX.

Apart from the main use case, the marking, tokenization and text extraction can be useful in other contexts such as
manual translation by a professional human translator or parsing.
"""
from .preprocessor import Preprocessor
from .marker import Marker
from .tokenizer import Tokenizer
from .translator import Translator
import logging

logging.getLogger('translatex').addHandler(logging.NullHandler())

__version__ = '0.2.0'
