"""Main module."""

import argparse
import subprocess
import sys

from translatex.marker import Marker
from translatex.tokenizer import Tokenizer


def main():
    """Console script for translatex."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "translatex.main.main")


    parser.add_argument('base_file', help="Name of the LaTeX source file")
    args = parser.parse_args()
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

    return


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
