# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from translatex import __version__

project = 'translatex'
copyright = "2023 Efe ERKEN"
author = 'Efe ERKEN'
version = __version__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.coverage',
    'sphinx.ext.graphviz',
    'sphinx_copybutton',
    'sphinx-prompt',
    'sphinx_last_updated_by_git'
]

templates_path = ['_templates']
exclude_patterns = []

autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
    'member-order': 'groupwise',
    'private-members': False,
    'special-members': '__init__'
}

graphviz_output_format = "svg"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_logo = '../../images/logo_small.png'
html_favicon = '../../images/logo_favicon.png'
