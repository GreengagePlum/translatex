"""preprocessor module test suite"""
import pytest
import re

from translatex.preprocessor import Preprocessor


def test_process(small_preprocessor):
    """Ensure Preprocessor processes correctly. This test verifies removal of manual replacement blocks."""
    p = small_preprocessor
    p.process()
    pattern = re.escape(p.indicator_format.split("{")[0]) + r"(?:\d+)"
    assert re.search(pattern, p.processed_latex)


def test_rebuild(small_preprocessor):
    """Ensure Preprocessor rebuilds correctly. This test verifies substitution for manual replacement blocks."""
    p = small_preprocessor
    p.process()
    p.rebuild()
    assert p.unprocessed_latex.find(r"\textit{Bienvenue en France !}") != -1
    assert p.unprocessed_latex.find(r"$x < 3$") != -1


def test_preserving(small_preprocessor):
    """Ensure Preprocessor preserves string identically when no process is asked to be made."""
    p = small_preprocessor
    base = p.base_latex
    p.process()
    p.rebuild(Preprocessor.DISABLE_SUBSTITUTION)
    after = p.unprocessed_latex
    assert base == after
