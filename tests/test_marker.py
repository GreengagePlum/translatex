"""marker module test suite"""
import pytest
import logging
import re
from translatex.marker import Marker
from TexSoup import TexSoup



def test_creation(small_marker):
    """Ensure Marker created correctly with all its properties"""
    m = small_marker
    assert m.base_latex
    assert m.unmarked_latex
    assert not m.marked_latex


def test_modification1(small_marker):
    """Ensure Marker updates correctly when modified"""
    m = small_marker
    base_before = m.base_latex
    m.marked_latex = "spam"
    assert m.base_latex == base_before
    assert not m.unmarked_latex
    assert m.marked_latex


def test_modification2(small_marker):
    """Ensure Marker updates correctly when modified"""
    m = small_marker
    base_before = m.base_latex
    m.unmarked_latex = "spam"
    assert m.base_latex == base_before
    assert m.unmarked_latex
    assert not m.marked_latex
    assert len(m._marker_store) == 0
    assert m.marker_count == 0


def test_modification3(small_marker):
    """Ensure Marker updates correctly when modified"""
    mod_value = "spam"
    m = small_marker
    m.base_latex = mod_value
    assert m.base_latex
    assert m.unmarked_latex == mod_value
    assert not m.marked_latex
    assert len(m._marker_store) == 0
    assert m.marker_count == 0


def test_marker_format(small_marker):
    """Ensure Marker format setter works correctly"""
    m = small_marker
    assert m.marker_format == Marker.DEFAULT_MARKER_FORMAT
    try:
        m.marker_format = "spam[]{}"
    except ValueError:
        pytest.fail()
    with pytest.raises(ValueError):
        m.marker_format = "[]{eggs"


def test_mark_node_name1(small_marker):
    """Ensure Marker marks LaTeX commands correctly"""
    m = small_marker
    m.mark()
    pattern = r"\\//(\d+)//{.*Hello.*}"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert m._marker_store[int(res.group(1))] == "textbf"


def test_mark_node_name2(small_marker):
    """Ensure Marker marks LaTeX named environments correctly"""
    m = small_marker
    m.mark()
    pattern = r"\\begin{//(\d+)//}"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert m._marker_store[int(res.group(1))] == "document"


def test_mark_node_contents1(math_marker):
    """Ensure Marker marks LaTeX unnamed environments (displaymath) correctly"""
    m = math_marker
    m.mark()
    pattern = r"\\\[//(\d+)//\\\]"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert "alpha" in m._marker_store[int(res.group(1))]


def test_mark_node_contents2(math_text_marker):
    """Ensure Marker marks LaTeX unnamed environments (displaymath) including text correctly"""
    m = math_text_marker
    m.mark()
    pattern = r"\\\[.*\\//(\d+)//{foo bar baz}.*\\\]"
    res = re.search(pattern, m.marked_latex, re.DOTALL)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert "text" == m._marker_store[int(res.group(1))]
    pattern = r"\\\[//(\d+)//.*\\\]"
    res = re.search(pattern, m.marked_latex, re.DOTALL)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert "Lambda" in m._marker_store[int(res.group(1))]


def test_mark_node_contents3(math_marker):
    """Ensure Marker content marker raises errors correctly"""
    m = math_marker
    n = TexSoup(m.base_latex).displaymath
    with pytest.raises(ValueError):
        m._mark_node_contents(n, 5, None)
    with pytest.raises(ValueError):
        m._mark_node_contents(n, 0, range(1, 5))
    try:
        m._mark_node_contents(n, 5, range(1, 5))
    except ValueError:
        pytest.fail("ValueError raised when it shouldn't have")


def test_mark_node_contents4(code_marker):
    """Ensure Marker marks LaTeX literal code environments correctly"""
    m = code_marker
    m.mark()
    pattern = r"\\begin.*\[language=Python\]//(\d+)//\\end"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert "sympy" in m._marker_store[int(res.group(1))]


def test_undo_marking(small_marker):
    """Ensure Marker preserves all details of the original string when unmarking operation is done"""
    m = small_marker
    m.mark()
    m.unmark()
    assert m.base_latex == m.unmarked_latex


def test_empty_marking(small_marker):
    """Ensure Marker raises an error when trying to mark an empty string"""
    m = small_marker
    m.unmarked_latex = ""
    with pytest.raises(ValueError):
        m.mark()


def test_empty_unmarking(small_marker):
    """Ensure Marker raises an error when trying to unmark an empty string"""
    m = small_marker
    with pytest.raises(ValueError):
        m.unmark()


def test_warning_unmarking(small_marker, caplog):
    """Ensure Marker warns about missing or altered markers on ``stderr``"""
    m = small_marker
    m.mark()
    m.unmark()
    with caplog.at_level(logging.ERROR):
        m.unmark()
    assert len(caplog.text) == 0
    m.marked_latex = "foo"
    with caplog.at_level(logging.ERROR):
        m.unmark()
    assert caplog.text
