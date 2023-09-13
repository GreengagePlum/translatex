#! /usr/bin/env python3

"""This script extracts changes from the changelog regarding a given version number."""

import argparse
import pathlib
import re
import sys

# Find the changelog in the current directory
changelog_found = False
for i in pathlib.Path(".").iterdir():
    name_match = re.match(r"changelog(\..*)?", i.name, re.IGNORECASE)
    if name_match:
        if changelog_found:
            print(
                "Found more than one changelog in the current directory, exiting...",
                file=sys.stderr,
            )
            sys.exit(1)
        changelog_path = i
        changelog_found = True

with changelog_path.open("r") as changelog:
    changelog_text = changelog.read()

# Setup  argparse to parse command line options
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "version_number", help="The version number to extract info about"
)
args = parser.parse_args()

# Check if given version number is actually a version number
if not re.match(r"^v?\d+\.\d+\.\d+$", args.version_number):
    print(
        "The given version number is not properly formatted, exiting...",
        file=sys.stderr,
    )
    sys.exit(1)

# Extract the info from the changelog related to the given version number
escaped_version_number = re.escape(
    args.version_number[1:]
    if args.version_number[0] == "v"
    else args.version_number
)
changelog_changes = re.search(
    rf"^(## \[{escaped_version_number}\].*?)^(## |\[.*?\]:)",
    changelog_text,
    re.DOTALL | re.MULTILINE,
)
changelog_hyperlink = re.search(
    rf"^\[{escaped_version_number}\].*", changelog_text, re.MULTILINE
)

# Print extracted info if found
if changelog_changes and changelog_hyperlink:
    print(changelog_changes[1] + changelog_hyperlink[0])
else:
    print(
        "Couldn't find any info about the given version number, exiting...",
        file=sys.stderr,
    )
    sys.exit(1)
