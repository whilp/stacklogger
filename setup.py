import sys

from setuptools import setup

meta = dict(
    name="stacklogger",
    version="0.1.0",
    description="A stack-aware logging extension",
    author="Will Maier",
    author_email="willmaier@ml1.net",
    py_modules=["stacklogger"],
    test_suite="tests.py",
    install_requires=["setuptools"],
    keywords="logging stack frame",
    url="http://packages.python.org/stacklogger",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python"
        "Topic :: System :: Logging",
    ],
)

# Automatic conversion for Python 3 requires distribute.
if sys.version_info >= (3,):
    meta.update(dict(
        use_2to3=True,
    ))

setup(**meta)
