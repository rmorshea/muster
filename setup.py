import os
from distutils.core import setup
from setuptools import find_packages


# Project
# -------

project = "muster"
summary = "a responsive classes framework"
author = "Ryan Morshead"
author_email = "ryan.morshead@gmail.com"
project_url = "https://github.com/rmorshea/muster"

keywords = [
    "attrs", "traits", "traitlets",
    "descriptors", "validation",
    "observe", "callbacks",
]

classifiers = [
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
]

# Details
# -------

details = """

"""

# Root Paths
# ----------

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, project)

# Package
# -------

packages = find_packages()

with open(os.path.join(root, "version.py")) as ver:
    namespace = {}
    exec(ver.read(), {}, namespace)

version = namespace["__version__"]


# Arguments
# ---------

setup_arguments = dict(
    name=project,
    author=author,
    author_email=author_email,
    url=project_url,
    version=version,
    packages=packages,
    description=summary,
    long_description=details,
    license="MIT",
    platforms="Linux, Mac OS X, Windows",
    keywords=keywords,
    classifiers=classifiers,
)

# Setup
# -----

setup(**setup_arguments)
