"""Configuration file for the Sphinx documentation builder."""

# -- Project information -----------------------------------------------------

project = 'Apolloscope'
project_copyright = '2021, Trong-Lanh Nguyen'
author = 'Trong-Lanh'

release = '0.2.0'


# -- General configuration ---------------------------------------------------

master_doc = 'home'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.mermaid',
]

pygments_style = 'monokai'

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
