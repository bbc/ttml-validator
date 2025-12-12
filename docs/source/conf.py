# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

sys.path.insert(0, str(Path('../../src').resolve()))

project = 'ttml-validator'
copyright = '2025, British Broadcasting Corporation'
author = 'Nigel Megitt'
version = release = '0.1.0'

# -- General configuration ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# include_patterns = [
#     'docs/',
#     'src/',
#     'test/',
# ]
templates_path = ['_templates']
exclude_patterns = [
    'build',
    'dist',
    'htmlcov'
]
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.apidoc',
    'sphinx.ext.napoleon',  # For Google and NumPy style docstrings
    'sphinx.ext.todo',
    'sphinx.ext.autosummary',
    'sphinx.ext.extlinks',
    # 'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.coverage',
    'sphinx.ext.graphviz',
]
apidoc_modules = [
    {'path': '../../src/constraintSets', 'destination': './modules/'},
    {'path': '../../src/preParseChecks', 'destination': './modules/'},
    {'path': '../../src/registries', 'destination': './modules/'},
    {'path': '../../src/schemas', 'destination': './modules/'},
    {'path': '../../src/validationLogging', 'destination': './modules/'},
    {'path': '../../src/xmlChecks', 'destination': './modules/'},
    {'path': '../../src', 'destination': './modules/'},
]
toc_object_entries_show_parents = 'hide'
add_module_names = False
modindex_common_prefix = ['src.']
autosummary_generate = True

language = 'en'
# master_doc = 'docs/index'
pygments_style = 'sphinx'
source_suffix = '.rst'

# -- Options for HTML output ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_static_path = ['_static']
