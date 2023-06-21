import pytest
from translatex.preprocessor import Preprocessor


@pytest.fixture
def small_preprocessor(small_marker) -> Preprocessor:
    return Preprocessor(r"""
    %@{ This is my manual replacement block
    \textbf{Welcome to France!}
    %@-------------------------------------
    \textit{Bienvenue en France !}
    % $x < 3$
    %@} Here is the end of the block
    """)
