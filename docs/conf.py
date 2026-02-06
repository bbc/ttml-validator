# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import yaml
import os
from pathlib import Path

sys.path.insert(0, str(Path('../src').resolve()))
sys.path.insert(0, str(Path('../').resolve()))

project = 'ttml-validator'
copyright = '2025, British Broadcasting Corporation'
author = 'Nigel Megitt'
version = release = '0.1.0'

# -- General configuration ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

include_patterns = [
    '**',
    '**/src',
    '**/test',
]
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
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.napoleon',  # For Google and NumPy style docstrings
    'sphinx.ext.todo',
    'sphinx.ext.autosummary',
    'sphinx.ext.extlinks',
    # 'sphinx.ext.linkcode',
    # 'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.coverage',
    'sphinx.ext.graphviz',
]
apidoc_modules = [
    {'path': '../src', 'destination': './source/modules/'},
]
toc_object_entries_show_parents = 'hide'
add_module_names = False
modindex_common_prefix = ['src.']
autosummary_generate = True
todo_include_todos = True

autodoc_default_options = {
    # 'no-index-entry': ['src'],
}

language = 'en'
# master_doc = 'docs/index'
pygments_style = 'sphinx'
source_suffix = '.rst'

napoleon_google_docstring = True

# -- Options for HTML output ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'bizstyle'
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "enable_search_shortcuts": True,
    "globaltoc_collapse": False,
    "sidebarwidth": "25rem",
}
html_static_path = ['_static']

html_context = {
    'current_version': version,
    'versions': [["0.1.0", "link to 0.1.0"], ["dev", "link to dev"]],
    'current_language': 'en',
    # 'languages': [["en", "link to en"]]  # not supporting languages
}

build_all_docs = os.environ.get("build_all_docs")
pages_root = os.environ.get("pages_root", "")

if build_all_docs is not None:
    current_language = os.environ.get("current_language")
    current_version = os.environ.get("current_version")

    html_context: dict[str, str | None | list[list[str]]] = {
        'current_language': current_language,
        # 'languages' : [],  # not supporting languages yet
        'current_version': current_version,
        'versions': [],
    }

    if (current_version == 'latest'):
        html_context['languages'].append(['en', pages_root])
        # Repeat for each supported language, this example German:
        # html_context['languages'].append(['de', pages_root+'/de'])

    if (current_language == 'en'):
        html_context['versions'] \
            .append(  # ty:ignore[possibly-missing-attribute]
                ['latest', pages_root])

    with open("versions.yaml", "r") as yaml_file:
        docs = yaml.safe_load(yaml_file)

    for version, details in docs.items():
        html_context['versions'] \
            .append(  # ty:ignore[possibly-missing-attribute]
                [version, pages_root+'/'+version+'/'+current_language])
