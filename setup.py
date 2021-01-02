from os import path
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


def get_long_description():
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
    return long_description


install_requires = [
    "aiofiles==0.6.0",
    "aio-msgpack-rpc==0.2.0",
    "DAWG==0.8.0",
    "diskcache==5.1.0",
    "fastapi==0.61.2",
    "lark-parser==0.8.9",
    "passlib[bcrypt]==1.7.4",
    "pyjwt==1.7.1",
    "python-multipart==0.0.5",
    "smart-open==4.0.1",
    "tabulate==0.8.7",
    "translitcodec==0.5.2",
    "typer==0.3.2",
    "ujson==4.0.1",
    "uvicorn==0.12.2",
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
    package_data={"": ["grammar.lark", "eff-long.txt.gz"]},
    include_package_data=True,
    entry_points={"console_scripts": ["entitykb=entitykb:cli"]},
    install_requires=install_requires,
    description="Python toolkit for rapidly developing knowledge bases",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/genomoncology/entitykb",
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
