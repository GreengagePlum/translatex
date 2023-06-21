import re

from translatex.preprocessor import Preprocessor
from translatex.marker import Marker
from translatex.tokenizer import Tokenizer


class Translator:
    pass


if __name__ == "__main__":
    base_file = "erken"
    with open(f"../../examples/{base_file}.tex") as f:
        p = Preprocessor(f.read())

    p.process()
    m = Marker.from_preprocessor(p)
    m.mark()
    t = Tokenizer.from_marker(m)
    t.tokenize()

    with open(f"../../examples/{base_file}_post.tex", "w+") as f:
        f.write(t.tokenized_string)

    a = Translator.from_tokenizer(t)
    a.translate()

    with open(f"../../examples/{base_file}_post2.tex", "w+") as f:
        f.write(a.translated_string)
