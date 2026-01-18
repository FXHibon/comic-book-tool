"""Setup configuration for cbr-fixer."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cbr-fixer",
    version="0.1.0",
    author="",
    description="A CLI tool to fix and convert CBR/CBZ comic book archive files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rarfile>=4.0",
    ],
    entry_points={
        "console_scripts": [
            "cbr-fixer=cbr_fixer.cli:main",
        ],
    },
)
