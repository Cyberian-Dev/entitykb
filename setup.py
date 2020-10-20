import sys

from setuptools import setup, find_packages

install_requires = [
    "pyahocorasick",
    "translitcodec",
    "lark-parser==0.8.9",
    "python-dateutil",
    "tabulate",
    "typer",
]

if sys.version_info[:2] == (3, 6):
    install_requires.append("dataclasses")

extras_require = {
    "rpc": ["aio-msgpack-rpc"],
    "http": ["fastapi", "aiofiles", "uvicorn >=0.11.7"],
}

setup(
    name="entitykb",
    version="0.2.1",
    author="Ian Maurer",
    author_email="ian@genomoncology.com",
    packages=find_packages("src/"),
    package_dir={"": "src"},
    package_data={"": ["*.lark"]},
    include_package_data=True,
    entry_points={"console_scripts": ["entitykb=entitykb.cli:app"]},
    install_requires=install_requires,
    extras_require=extras_require,
    description="Rules-based Named Entity Recognition and Linking",
    long_description="Rules-based Named Entity Recognition and Linking",
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
