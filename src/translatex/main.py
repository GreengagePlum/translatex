"""Main module."""
import argparse
import sys

from translatex import __version__
from translatex.preprocessor import Preprocessor
from translatex.marker import Marker
from translatex.tokenizer import Tokenizer
from translatex.translator import Translator

DEFAULT_INTER_FILE_PRE: str = "~"
DEFAULT_INTER_FILE_EXT: str = "txt"


def main():
    """Console script for translatex."""
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}", help="Version number")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug option to generate intermediary files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print additional info on <stderr>")
    mutually_exclusive_group = parser.add_mutually_exclusive_group()
    mutually_exclusive_group.add_argument("--dry-run", action="store_true",
                                          help="Don't translate (no API call), just run the chain of operations")
    mutually_exclusive_group.add_argument("-s", "--stop", choices=["Preprocessor", "Marker", "Tokenizer", "Translator"],
                                          help="Stop at specified stage and write its result to output")
    parser.add_argument("--no-pre", action="store_false",
                        help="Don't do manual substitution during preprocessing stage")
    parser.add_argument("-mf", "--marker-format", help="Marker format to use during marking stage")
    parser.add_argument("-tf", "--token-format", help="Token format to use during tokenization stage")
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w+'), default=sys.stdout)
    args = parser.parse_args()
    base_file: str = DEFAULT_INTER_FILE_PRE + args.infile.name.split("/")[-1].split(".")[0]
    p = Preprocessor(args.infile.read())
    p.process()
    if args.verbose:
        print("---- Preprocessor info ----", p, file=sys.stderr)
    if args.stop == "Preprocessor":
        args.outfile.write(p.processed_latex)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_processed." + DEFAULT_INTER_FILE_EXT, "w+") as f:
            f.write(p.processed_latex)
    m = Marker.from_preprocessor(p)
    if args.marker_format:
        m.marker_format = args.marker_format
    m.mark()
    if args.verbose:
        print("---- Marker info ----", m, file=sys.stderr)
    if args.stop == "Marker":
        args.outfile.write(m.marked_latex)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_marked." + DEFAULT_INTER_FILE_EXT, "w+") as f:
            f.write(m.marked_latex)
    t = Tokenizer.from_marker(m)
    if args.token_format:
        t.token_format = args.token_format
    t.tokenize()
    if args.verbose:
        print("---- Tokenizer info ----", t, file=sys.stderr)
    if args.stop == "Tokenizer":
        args.outfile.write(t.tokenized_string)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_tokenized." + DEFAULT_INTER_FILE_EXT, "w+") as f:
            f.write(t.tokenized_string)
    a = Translator.from_tokenizer(t)
    if not args.dry_run:
        a.translate()
        if args.verbose:
            print("---- Translator info ----", a, file=sys.stderr)
        if args.stop == "Translator":
            args.outfile.write(a.translated_string)
            sys.exit()
        if args.debug:
            with open(f"{base_file}_translated." + DEFAULT_INTER_FILE_EXT, "w+") as f:
                f.write(a.translated_string)
        t.update_from_translator(a)
    else:
        t.tokenized_string = a.tokenized_string
    t.detokenize()
    m.update_from_tokenizer(t)
    m.unmark()
    p.update_from_marker(m)
    p.rebuild(args.no_pre)
    args.outfile.write(p.unprocessed_latex)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
