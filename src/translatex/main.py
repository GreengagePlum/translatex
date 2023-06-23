"""Main module."""

import argparse
import subprocess
import sys

from translatex.preprocessor import Preprocessor
from translatex.marker import Marker
from translatex.tokenizer import Tokenizer
from translatex.translator import Translator


def demo(args):
    base_file: str = args.base_file
    base_file = base_file.split(".tex")[0]
    with open(f"{base_file}.tex") as f:
        m = Marker(f.read())
    m.mark()
    with open(f"{base_file}_marked.tex", "w+") as f:
        f.write(m.marked_latex)
    t = Tokenizer(m.marked_latex)
    t.tokenize()
    with open(f"{base_file}_tokenized.tex", "w+") as f:
        f.write(t.tokenized_string)
    subprocess.run(['code', "--wait", f"{base_file}_tokenized.tex"])
    with open(f"{base_file}_tokenized.tex") as f:
        t.tokenized_string = f.read()
    t.detokenize()
    m.marked_latex = t.marked_string
    m.unmark()
    with open(f"{base_file}_result.tex", "w+") as f:
        f.write(m.unmarked_latex)
    print("Process complete")


def translatex(args):
    base_file: str = args.base_file
    base_file = base_file.split(".tex")[0]
    with open(f"{base_file}.tex") as f:
        p = Preprocessor(f.read())
    p.process()
    if args.debug:
        with open(f"{base_file}_processed.tex", "w+") as f:
            f.write(p.processed_latex)
    m = Marker.from_preprocessor(p)
    m.mark()
    if args.debug:
        with open(f"{base_file}_marked.tex", "w+") as f:
            f.write(m.marked_latex)
    t = Tokenizer.from_marker(m)
    t.tokenize()
    if args.debug:
        with open(f"{base_file}_tokenized.tex", "w+") as f:
            f.write(t.tokenized_string)
    a = Translator.from_tokenizer(t)
    a.translate()
    if args.debug:
        with open(f"{base_file}_translated.tex", "w+") as f:
            f.write(a.translated_string)
    t.update_from_translator(a)
    t.detokenize()
    m.update_from_tokenizer(t)
    m.unmark()
    p.update_from_marker(m)
    p.rebuild()
    with open(f"{base_file}_result.tex", "w+") as f:
        f.write(p.unprocessed_latex)
    print("Process complete")


def main():
    """Console script for translatex."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "translatex.main.main")

    parser.add_argument("base_file", help="Name of the LaTeX source file")
    parser.add_argument("-d", "--debug", action="store_true", help="Name of the LaTeX source file")
    args = parser.parse_args()
    translatex(args)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
