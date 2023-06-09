import re

import pytest
from translatex import marker


@pytest.fixture
def small_marker():
    return marker.Marker(r"""
    \begin{document}
    \textbf{\color{\text{blue}} Hello world}
    \end{document}
    """)


@pytest.fixture
def math_marker():
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
    return marker.Marker(r"""
    \begin{document}
    \[
    \Lambda\,(\mathcal{P}) \geqslant \, \; \sum_{72}^{10}
    \frac{\int_{-151}^{69} - \frac{3\mu}{2} + 4x - \pi + 2 \, \: \;
    \text{foo bar baz}
    \mathrm{d}x}{\sum_{10}^{72} - 5\alpha + \frac{x}{7} + 7 - \frac{18}{7\sigma} - \frac{5}{\alpha}} \, \: \;
    \mathrm{,}
    \]
    \end{document}
    """)


def test_creation(small_marker):
    m = small_marker
    assert m.base_latex
    assert m.unmarked_latex
    assert not m.marked_latex


def test_modification1(small_marker):
    m = small_marker
    base_before = m.base_latex
    m.marked_latex = "spam"
    assert m.base_latex == base_before
    assert not m.unmarked_latex
    assert m.marked_latex


def test_modification2(small_marker):
    m = small_marker
    base_before = m.base_latex
    m.unmarked_latex = "spam"
    assert m.base_latex == base_before
    assert m.unmarked_latex
    assert not m.marked_latex
    assert len(m._marker_store) == 0
    assert m.marker_count == 0


def test_modification3(small_marker):
    mod_value = "spam"
    m = small_marker
    m.base_latex = mod_value
    assert m.base_latex
    assert m.unmarked_latex == mod_value
    assert not m.marked_latex
    assert len(m._marker_store) == 0
    assert m.marker_count == 0


def test_marker_format(small_marker):
    m = small_marker
    assert m.marker_format == marker.Marker.DEFAULT_MARKER_FORMAT
    try:
        m.marker_format = "spam[]{}"
    except ValueError:
        pytest.fail()
    with pytest.raises(ValueError):
        m.marker_format = "[]{eggs"


def test_mark_node_name1(small_marker):
    m = small_marker
    m.do_marking()
    pattern = r"[\s\S]*\s\\//(\d+)//{.*Hello.*}"
    res = re.match(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert m._marker_store[int(res.group(1))] == "textbf"


def test_mark_node_name2(small_marker):
    m = small_marker
    m.do_marking()
    pattern = r"[\s\S]*\\begin{//(\d+)//}"
    res = re.match(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert m._marker_store[int(res.group(1))] == "document"


def test_mark_node_contents1(math_marker):
    m = math_marker
    m.do_marking()
    pattern = r"[\s\S]*\\\[//(\d+)//\\\]"
    res = re.match(pattern, m.marked_latex)
    assert res
    assert int(res.group(1)) in m._marker_store.keys()
    assert "alpha" in m._marker_store[int(res.group(1))]


def test_mark_node_contents2(math_text_marker):
    # m = math_text_marker
    # m.do_marking()
    # pattern = r"[\s\S]*\\\[[[\s\S]*[\]?//(\d+)//]*{foo bar baz}\\\]"
    # res = re.match(pattern, m.marked_latex)
    # assert res
    # assert int(res.group(1)) in m._marker_store.keys()
    # assert "Lambda" in m._marker_store[int(res.group(1))]
    pass
