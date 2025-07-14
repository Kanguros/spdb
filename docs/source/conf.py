# Sphinx configuration for SPDB documentation
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))


project = "SPDB"
author = "SPDB Contributors"
release = "0.1.0"

# Use README.md from root as main page
master_doc = "index"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_pydantic",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "linkify",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# Use sphinxawesome-theme for modern look
html_theme = "sphinxawesome_theme"
html_title = "SPDB Documentation"
html_show_sourcelink = False

# Autodoc settings
autoclass_content = "both"
autodoc_member_order = "bysource"

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# MyST settings
myst_heading_anchors = 3
