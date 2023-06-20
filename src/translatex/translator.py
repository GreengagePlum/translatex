import re

from translatex.marker import Marker
from translatex.tokenizer import Tokenizer


class Translator:
    pass


if __name__ == "__main__":
    base_file = "translatex"
    with open(f"../../examples/{base_file}.tex") as f:
        m = Marker(f.read())

    m.mark()
    with open(f"../../examples/{base_file}_post.tex", "w+") as f:
        f.write(m.marked_latex)

    t = Tokenizer(m.marked_latex)
    t.tokenize()
    with open(f"../../examples/{base_file}_post2.tex", "w+") as f:
        f.write(t.tokenized_string)
