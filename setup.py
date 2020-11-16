import re
import sys
from pathlib import Path

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    version = Path(package, "__version__.py").read_text()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", version).group(1)


install_requires = [
    "aio-msgpack-rpc",
    "fastapi",
    "pyahocorasick",
    "translitcodec",
    "lark-parser==0.8.9",
    "python-dateutil",
    "tabulate",
    "typer",
    "uvicorn >=0.11.7",
]

if sys.version_info[:2] == (3, 6):
    install_requires.append("dataclasses")

setup(
    name="entitykb",
    python_requires=">=3.6",
    version=get_version("src/entitykb"),
    author="Ian Maurer",
    author_email="ian@genomoncology.com",
    packages=find_packages("src/"),
    package_dir={"": "src"},
    package_data={"": ["*.lark"]},
    include_package_data=True,
    entry_points={"console_scripts": ["entitykb=entitykb:cli"]},
    install_requires=install_requires,
    description="Python toolkit for building Knowledge Bases",
    long_description="Python toolkit for building Knowledge Bases",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
    ],
)
