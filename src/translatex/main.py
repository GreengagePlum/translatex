"""Translatex: A LaTeX translator.

The entry point to the program. The given LaTeX file is run through multiple processes such as preprocessing, marking,
and tokenization to replace all LaTeX syntax constructs by tokens that ideally won't be modified by automatic
translators. That, for the purpose of translating LaTeX source code automatically to any specified language while
keeping it error free and compilable at the end, resulting in the same looking file.
"""

import argparse
import sys
from pathlib import Path
import logging

from . import __version__
from .preprocessor import Preprocessor
from .marker import Marker
from .tokenizer import Tokenizer
from .translator import Translator, TRANSLATION_SERVICES_BY_NAME

DEFAULT_INTER_FILE_PRE: str = "_"
DEFAULT_INTER_FILE_EXT: str = ".txt"

log = logging.getLogger(__name__)


def translatex(args: argparse.Namespace) -> None:
    """Run the translatex pipeline on a LaTeX source file."""
    base_file: str = DEFAULT_INTER_FILE_PRE + Path(args.infile.name).stem
    p = Preprocessor(args.infile.read())
    p.process()
    log.debug("---- Preprocessor info ---- %s", p)
    if args.stop == "Preprocessor":
        args.outfile.write(p.processed_latex)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_processed{DEFAULT_INTER_FILE_EXT}", "w+") as f:
            f.write(p.processed_latex)
        with open(f"{base_file}_indicator_store{DEFAULT_INTER_FILE_EXT}", "w+") as f:
            f.write(p.dump_store())
    m = Marker.from_preprocessor(p)
    if args.marker_format:
        m.marker_format = args.marker_format
    m.mark()
    log.debug("---- Marker info ---- %s", m)
    if args.stop == "Marker":
        args.outfile.write(m.marked_latex)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_marked{DEFAULT_INTER_FILE_EXT}", "w+") as f:
            f.write(m.marked_latex)
        with open(f"{base_file}_marker_store{DEFAULT_INTER_FILE_EXT}", "w+") as f:
            f.write(m.dump_store())
    t = Tokenizer.from_marker(m)
    if args.token_format:
        t.token_format = args.token_format
    t.tokenize()
    log.debug("---- Tokenizer info ---- ")
    if args.stop == "Tokenizer":
        args.outfile.write(t.tokenized_string)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_tokenized{DEFAULT_INTER_FILE_EXT}", "w+") as f:
            f.write(t.tokenized_string)
        with open(f"{base_file}_token_store{DEFAULT_INTER_FILE_EXT}", "w+") as f:
            f.write(t.dump_store())
    a = Translator.from_tokenizer(t)
    if not args.dry_run:
        service = TRANSLATION_SERVICES_BY_NAME[args.service]
        a.translate(service=service, source_lang=args.src_lang,
                    destination_lang=args.dest_lang)
        if args.stop == "Translator":
            args.outfile.write(a.translated_string)
            sys.exit()
        if args.debug:
            with open(f"{base_file}_translated{DEFAULT_INTER_FILE_EXT}", "w+") as f:
                f.write(a.translated_string)
        t.update_from_translator(a)
    else:
        t.tokenized_string = a.tokenized_string
    log.debug("---- Translator info ---- %s", a)
    t.detokenize()
    m.update_from_tokenizer(t)
    m.unmark()
    p.update_from_marker(m)
    p.rebuild(args.no_pre)
    args.outfile.write(p.unprocessed_latex)
    if args.outfile.name != "<stdout>":
        log.info("Translated LaTeX file written to %s", args.outfile.name)


def main() -> None:
    """Console script for translatex."""
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}",
                        help="Version number")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Debug option to generate intermediary files")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print additional info on <stderr>")
    mutually_exclusive_group = parser.add_mutually_exclusive_group()
    mutually_exclusive_group.add_argument(
        "--dry-run", action="store_true",
        help="Don't translate (no API call), just run the chain of operations")
    mutually_exclusive_group.add_argument(
        "-s", "--stop",
        choices=["Preprocessor", "Marker", "Tokenizer", "Translator"],
        help="Stop at the end of the specified stage and write its result to output")
    parser.add_argument("--no-pre", action="store_false",
                        help="Don't do manual substitution during preprocessing stage")
    parser.add_argument("-mf", "--marker-format",
                        help="Marker format to use during marking stage")
    parser.add_argument("-tf", "--token-format",
                        help="Token format to use during tokenization stage")
    parser.add_argument("-sl", "--src-lang",
                        default=Translator.DEFAULT_SOURCE_LANG,
                        help="Input's language")
    parser.add_argument("-dl", "--dest-lang",
                        default=Translator.DEFAULT_DEST_LANG,
                        help="Output's language")
    parser.add_argument("--service",
                        choices=list(TRANSLATION_SERVICES_BY_NAME.keys()),
                        default=Translator.DEFAULT_SERVICE.name, type=str,
                        help="Translation service to use")
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?',
                        type=argparse.FileType('w+'), default=sys.stdout)
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    translatex(args)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
