# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

<<<<<<< HEAD
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

=======
>>>>>>> cc770a46a846759bed92276263d1831765d55bf0
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'datamood'
copyright = '2025, seungwoo37, lim57, alrka-code, xnhwxn, piven12'
author = 'seungwoo37, lim57, alrka-code, xnhwxn, piven12'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

<<<<<<< HEAD
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon', # Google/Numpy 스타일 docstring 지원
    'sphinx.ext.viewcode'
]
=======
extensions = []
>>>>>>> cc770a46a846759bed92276263d1831765d55bf0

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

<<<<<<< HEAD
html_theme = 'sphinx_rtd_theme'
=======
html_theme = 'alabaster'
>>>>>>> cc770a46a846759bed92276263d1831765d55bf0
html_static_path = ['_static']
