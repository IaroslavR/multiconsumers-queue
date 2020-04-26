"""Sphinx configuration."""
import os
from typing import MutableMapping

import sphinx_rtd_theme  # noqa: F401


def get_meta() -> MutableMapping:
    """Get project metadata from pyproject.toml file.

    Returns:
        MutableMapping
    """
    import toml

    toml_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")

    with open(toml_path) as fopen:
        pyproject = toml.load(fopen)

    return pyproject


meta = get_meta()

project = meta["tool"]["poetry"]["name"]
author = ",".join(meta["tool"]["poetry"]["authors"])
copyright = f"2020, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "m2r",
]

# The short X.Y version
version = meta["tool"]["poetry"]["version"]
# The full version, including alpha/beta/rc tags
release = version

# Autodoc Settings
autodoc_default_options = {"member-order": "bysource", "undoc-members": True}

# source_suffix = ".rst"
source_suffix = [".rst", ".md"]
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_options = {"navigation_depth": -1}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# Output file base name for HTML help builder.
htmlhelp_basename = project


# Set master doc
master_doc = "index"
