# Sphinx configuration for SPDB documentation
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))


project = "SPDB"
author = "Kamil Urbanek"
release = "0.1.0"

# Use README.md from root as main page
master_doc = "index"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.autodoc_pydantic",
]
# MyST settings
myst_heading_anchors = 3

# autodoc_pydantic settings
autodoc_pydantic_model_show_json = True
autodoc_pydantic_model_show_config_summary = True
autodoc_pydantic_model_show_field_summary = True
autodoc_pydantic_model_show_validator_summary = True
autodoc_pydantic_model_show_field_constraints = True
autodoc_pydantic_model_show_validator_constraints = True
autodoc_pydantic_model_show_json_error_examples = True

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


# Use sphinx-book-theme for modern look
html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/your-repo/spdb",
    "use_repository_button": True,
    "path_to_docs": "docs/source",
}

html_title = "SPDB Documentation"
html_show_sourcelink = False

# Autodoc settings
autoclass_content = "both"
autodoc_member_order = "bysource"

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False

# MyST settings
myst_heading_anchors = 3
