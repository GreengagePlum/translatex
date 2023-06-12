"""marker module test suite"""
import re

import pytest
from translatex import marker
from TexSoup import TexSoup


@pytest.fixture
def small_marker():
    """Marker instance with short LaTeX string"""
    return marker.Marker(r"""
    \begin{document}
    \textbf{\color{\text{blue}} Hello world}
    \end{document}
    """)


@pytest.fixture
def math_marker():
    """Marker instance with LaTeX string including a pure math environment"""
    return marker.Marker(r"""
    \begin{document}
    \[
    \Lambda\,(\mathcal{P}) \geqslant \, \; \sum_{72}^{10}
    \frac{\int_{-151}^{69} - \frac{3\mu}{2} + 4x - \pi + 2 \, \: \;
    \mathrm{d}x}{\sum_{10}^{72} - 5\alpha + \frac{x}{7} + 7 - \frac{18}{7\sigma} - \frac{5}{\alpha}} \, \: \;
    \mathrm{,}
    \]
    \end{document}
    """)


@pytest.fixture
def math_text_marker():
    """Marker instance with LaTeX string including a math environment with text"""
    return marker.Marker(r"""
    \begin{document}
    \[
    \Lambda\,(\mathcal{P}) \geqslant \, \; \sum_{72}^{10}
    \frac{\int_{-151}^{69} - \frac{3\mu}{2} + 4x - \pi + 2 \, \: \;
    \mathrm{d}x}{\sum_{10}^{72} - 5\alpha + \frac{x}{7} + 7 - \frac{18}{7\sigma} - \frac{5}{\alpha}} \, \: \;
    \mathrm{,}
    \text{foo bar baz}
    \]
    \end{document}
    """)


@pytest.fixture
def code_marker():
    """Marker instance with LaTeX string including a literal code environment"""
    return marker.Marker(r"""
    \begin{document}
    \begin{lstlisting}[language=Python]
    import sympy as sp

    x = sp.Symbol('x')
    f = x**2
    int_f = sp.integrate(f, x)

    print(int_f)
    \end{lstlisting}
    \end{document}
    """)


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
    assert m.marker_format == marker.Marker.DEFAULT_MARKER_FORMAT
    try:
        m.marker_format = "spam[]{}"
    except ValueError:
        pytest.fail()
    with pytest.raises(ValueError):
        m.marker_format = "[]{eggs"


def test_mark_node_name1(small_marker):
    """Ensure Marker marks LaTeX commands correctly"""
    m = small_marker
    m.do_marking()
    pattern = r"\\//(\d+)//{.*Hello.*}"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert m._marker_store[int(res.group(1))] == "textbf"


def test_mark_node_name2(small_marker):
    """Ensure Marker marks LaTeX named environments correctly"""
    m = small_marker
    m.do_marking()
    pattern = r"\\begin{//(\d+)//}"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert m._marker_store[int(res.group(1))] == "document"


def test_mark_node_contents1(math_marker):
    """Ensure Marker marks LaTeX unnamed environments (displaymath) correctly"""
    m = math_marker
    m.do_marking()
    pattern = r"\\\[//(\d+)//\\\]"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert "alpha" in m._marker_store[int(res.group(1))]


def test_mark_node_contents2(math_text_marker):
    """Ensure Marker marks LaTeX unnamed environments (displaymath) including text correctly"""
    m = math_text_marker
    m.do_marking()
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
    m.do_marking()
    pattern = r"\\begin.*\[language=Python\]//(\d+)//\\end"
    res = re.search(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert "sympy" in m._marker_store[int(res.group(1))]


def test_undo_marking(small_marker):
    """Ensure Marker preserves all details of the original string when unmarking operation is done"""
    m = small_marker
    m.do_marking()
    m.undo_marking()
    assert m.base_latex == m.unmarked_latex
