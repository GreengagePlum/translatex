"""TransLaTeX: A LaTeX translator.

The entry point to the program. The given LaTeX file is run through multiple processes such as preprocessing, marking,
and tokenization to replace all LaTeX syntax constructs by tokens that ideally won't be modified by automatic
translators. That, for the purpose of translating LaTeX source code automatically to any specified language while
keeping it error free and compilable at the end, resulting in the same looking file.
"""

import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .marker import Marker
from .preprocessor import Preprocessor
from .tokenizer import Tokenizer
from .translator import (Translator, TRANSLATION_SERVICE_CLASSES,
                         add_custom_translation_services)

DEFAULT_INTER_FILE_PRE: str = "_"
DEFAULT_INTER_FILE_EXT: str = ".txt"

log = logging.getLogger("translatex.main")


def translatex(args: argparse.Namespace) -> None:
    """Run the TransLaTeX pipeline on a LaTeX source file."""
    if args.custom_api:
        add_custom_translation_services(args.custom_api)
    if args.service not in TRANSLATION_SERVICE_CLASSES:
        log.error("The given service is not available. "
                  "Please choose one of the following: %s",
                  ", ".join(TRANSLATION_SERVICE_CLASSES.keys()))
        sys.exit(1)
    base_file: str = DEFAULT_INTER_FILE_PRE + Path(args.infile.name).stem
    p = Preprocessor(args.infile.read())
    args.infile.close()
    p.process()
    log.info("---- Preprocessor info ---- %s", p)
    if args.stop == "Preprocessor":
        args.outfile.write(p.processed_latex)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_processed{DEFAULT_INTER_FILE_EXT}", "w") as f:
            f.write(p.processed_latex)
        with open(f"{base_file}_indicator_store{DEFAULT_INTER_FILE_EXT}", "w") as f:
            f.write(p.dump_store())
    m = Marker.from_preprocessor(p)
    if args.marker_format:
        m.marker_format = args.marker_format
    m.mark()
    log.info("---- Marker info ---- %s", m)
    if args.stop == "Marker":
        args.outfile.write(m.marked_latex)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_marked{DEFAULT_INTER_FILE_EXT}", "w") as f:
            f.write(m.marked_latex)
        with open(f"{base_file}_marker_store{DEFAULT_INTER_FILE_EXT}", "w") as f:
            f.write(m.dump_store())
    t = Tokenizer.from_marker(m)
    if args.token_format:
        t.token_format = args.token_format
    t.tokenize()
    log.info("---- Tokenizer info ---- %s", t)
    if args.stop == "Tokenizer":
        args.outfile.write(t.tokenized_string)
        sys.exit()
    if args.debug:
        with open(f"{base_file}_tokenized{DEFAULT_INTER_FILE_EXT}", "w") as f:
            f.write(t.tokenized_string)
        with open(f"{base_file}_token_store{DEFAULT_INTER_FILE_EXT}", "w") as f:
            f.write(t.dump_store())
    a = Translator.from_tokenizer(t)
    if not args.dry_run:
        a.translate(service=TRANSLATION_SERVICE_CLASSES[args.service](),
                    source_lang=args.src_lang,
                    destination_lang=args.dest_lang)
        if args.stop == "Translator":
            args.outfile.write(a.translated_string)
            sys.exit()
        if args.debug:
            with open(f"{base_file}_translated{DEFAULT_INTER_FILE_EXT}", "w") as f:
                f.write(a.translated_string)
        t.update_from_translator(a)
    else:
        t.tokenized_string = a.tokenized_string
    log.info("---- Translator info ---- %s", a)
    t.detokenize()
    m.update_from_tokenizer(t)
    m.unmark()
    p.update_from_marker(m)
    p.rebuild(args.no_pre)
    args.outfile.write(p.unprocessed_latex)
    if args.outfile != sys.stdout:
        log.info("Translated LaTeX file written to %s", args.outfile.name)
    args.outfile.close()


def parse_args(args) -> argparse.Namespace:
    """Argument parser for TransLaTeX."""
    parser = argparse.ArgumentParser(
        prog="translatex",
        description=__doc__, allow_abbrev=False)
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}",
                        help="Version number")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Generate intermediary files and output all logs")
    parser.add_argument("-v", "--verbose", action="count",
                        default=0, help="Output information logs to see details on what's going on")
    mutually_exclusive_group = parser.add_mutually_exclusive_group()
    mutually_exclusive_group.add_argument(
        "-n", "--dry-run", action="store_true",
        help="Don't translate (no API call), just run the chain of operations")
    mutually_exclusive_group.add_argument(
        "-s", "--stop",
        choices=["Preprocessor", "Marker", "Tokenizer", "Translator"],
        help="Stop at the end of the specified stage and write its result to output")
    parser.add_argument("--no-pre", action="store_false",
                        help="Don't do manual substitution during preprocessing stage")
    parser.add_argument("-mf", "--marker-format",
                        default=Marker.DEFAULT_MARKER_FORMAT,
                        help="Marker format to use during marking stage (default: %(default)s)")
    parser.add_argument("-tf", "--token-format",
                        default=Tokenizer.DEFAULT_TOKEN_FORMAT,
                        help="Token format to use during tokenization stage (default: %(default)s)")
    parser.add_argument("-sl", "--src-lang",
                        default=Translator.DEFAULT_SOURCE_LANG,
                        help="Input's language (default: %(default)s)")
    parser.add_argument("-dl", "--dest-lang",
                        default=Translator.DEFAULT_DEST_LANG,
                        help="Output's language (default: %(default)s)")
    parser.add_argument(
        "-ca", "--custom_api", type=argparse.FileType('r'),
        help="Python file that provides a custom translation service class")
    service_choices = tuple(TRANSLATION_SERVICE_CLASSES.keys()) + ('Custom service...',)
    parser.add_argument(
        "--service",
        default=Translator.DEFAULT_SERVICE.name, type=str,
        help=f"Translation service to use {service_choices} (default: %(default)s)")
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin,
                        help="File to read LaTeX from")
    parser.add_argument('outfile', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help="File to output the processed LaTeX (can be non existant)")
    return parser.parse_args(args)


def main():
    """Console script for TransLaTeX.

    Logging is set as follows in case TransLaTeX is used as a program by invoking this main script. Otherwise,
    if TransLaTeX is imported as a module, logging stays quiet by the help of a ``NullHandler`` just like a library
    needs to do.

    If the debug option is set, the root logger is configured to ``DEBUG`` level (this option also causes the generation of
    intermediary files later). This is the ultimate logging option.

    Else if verbose level 1 is set, only TransLaTeX's logger is configured meaning only
    this program's logs are output and none of the external imported modules'.

    Else if verbose level 2 is set, similarly to the debug option, the root logger is configured but to ``INFO`` level
    meaning both TransLaTeX's and the imported modules' logs are output (to note: no intermediary files in this case).

    Lastly, if none of these options are set, the root logger is configured to ``WARNING`` level. This helps to display
    any errors and issues that arise during execution. Don't forget to redirect these logs on ``stderr`` via
    ``2> /dev/null`` or equivalent if you only want the LaTeX output when you're using ``stdout`` as the output
    destination.

    In short the levels of information in the logs increase as follows according to the given options: ``-v``,
    ``-vv``, ``-d``.
    """
    args = parse_args(sys.argv[1:])
    console_small = logging.StreamHandler()
    console_small.setFormatter(logging.Formatter("%(name)s: %(levelname)s %(message)s"))
    console_full = logging.StreamHandler()
    console_full.setFormatter(
        logging.Formatter(fmt="< %(asctime)-26s | %(name)-24s | %(levelname)-8s >\n%(message)s\n",
                          datefmt="%Y-%m-%d %H:%M:%S %z"))
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, handlers=[console_full])
    elif args.verbose == 1:
        package_logger = logging.getLogger("translatex")
        package_logger.setLevel(logging.INFO)
        package_logger.addHandler(console_small)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.INFO, handlers=[console_full])
    else:
        logging.basicConfig(level=logging.WARNING, handlers=[console_small])
    translatex(args)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
