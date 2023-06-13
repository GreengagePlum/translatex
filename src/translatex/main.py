"""Main module."""

import argparse
import sys


def main():
    """Console script for translatex."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "translatex.translatex.main")
    return


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
