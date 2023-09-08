from textwrap import dedent

import pytest

from translatex.marker import Marker


@pytest.fixture
def small_marker() -> Marker:
    """Marker instance with short LaTeX string"""
    return Marker(
        dedent(
            r"""
    \begin{document}
    \textbf{\color{\text{blue}} The color blue}
    \verb+hello+
    \end{document}
    """
        )
    )


@pytest.fixture
def math_marker():
    """Marker instance with LaTeX string including a pure math environment"""
    return Marker(
        dedent(
            r"""
    \begin{document}
    \[
    \Lambda\,(\mathcal{P}) \geqslant \, \; \sum_{72}^{10}
    \frac{\int_{-151}^{69} - \frac{3\mu}{2} + 4x - \pi + 2 \, \: \;
    \mathrm{d}x}{\sum_{10}^{72} - 5\alpha + \frac{x}{7} + 7 - \frac{18}{7\sigma} - \frac{5}{\alpha}} \, \: \;
    \mathrm{,}
    \]
    \end{document}
    """
        )
    )


@pytest.fixture
def math_text_marker():
    """Marker instance with LaTeX string including a math environment with text"""
    return Marker(
        r"""
    \begin{document}
    \[
    \Lambda\,(\mathcal{P}) \geqslant \, \; \sum_{72}^{10}
    \frac{\int_{-151}^{69} - \frac{3\mu}{2} + 4x - \pi + 2 \, \: \;
    \mathrm{d}x}{\sum_{10}^{72} - 5\alpha + \frac{x}{7} + 7 - \frac{18}{7\sigma} - \frac{5}{\alpha}} \, \: \;
    \mathrm{,}
    \text{foo bar baz}
    \]
    \end{document}
    """
    )


@pytest.fixture
def code_marker():
    """Marker instance with LaTeX string including a literal code environment"""
    return Marker(
        r"""
    \begin{document}
    \begin{lstlisting}[language=Python]
    import sympy as sp

    x = sp.Symbol('x')
    f = x**2
    int_f = sp.integrate(f, x)

    print(int_f)
    \end{lstlisting}
    \end{document}
    """
    )
