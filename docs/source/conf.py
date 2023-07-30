# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from translatex import __version__

project = 'TransLaTeX'
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

html_theme_options = {
    "source_edit_link": "https://gitlab.math.unistra.fr/cassandre/translatex/edit/main/docs/source/{filename}",
    "footer_icons": [
        {
            "name": "GitLab",
            "url": "https://gitlab.math.unistra.fr/cassandre/translatex",
            "html": """
                    <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 256 256" height="1em"
                    width="1em" xmlns="http://www.w3.org/2000/svg">
                    
                    <path d="M220.23,110.84,128,176,35.77,110.84,53.5,43A3.93,3.93,0,0,1,61,42.62L80.65,
                    96h94.7L195,42.62a3.93,3.93,0,0,1,7.53.38Z" opacity="0.2">
                    </path>
                    
                    <path d="M230.15,117.1,210.25,41a11.94,11.94,0,0,0-22.79-1.11L169.78,88H86.22L68.54,39.87A11.94,
                    11.94,0,0,0,45.75,41L25.85,117.1a57.19,57.19,0,0,0,22,61l73.27,51.76a11.91,11.91,0,0,0,13.74,
                    0l73.27-51.76A57.19,57.19,0,0,0,230.15,117.1ZM58,57.5,73.13,98.76A8,8,0,0,0,80.64,104h94.72a8,8,0,
                    0,0,7.51-5.24L198,57.5l13.07,50L128,166.21,44.9,107.5ZM40.68,124.11,114.13,176,93.41,190.65,57.09,
                    165A41.06,41.06,0,0,1,40.68,124.11Zm87.32,91-20.73-14.65L128,185.8l20.73,14.64ZM198.91,165l-36.32,
                    25.66L141.87,176l73.45-51.9A41.06,41.06,0,0,1,198.91,165Z">
                    </path>
                    
                    </svg>
            """,
            "class": "",
        },
    ],
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_logo = '../../images/logo_small.png'
html_favicon = '../../images/logo_favicon.png'
