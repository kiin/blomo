import re

from pathlib import Path
from setuptools import setup, find_packages

with open("README.md") as readme:
    long_description = readme.read()


def get_version():
    """Get version number from __init__.py"""
    version_file = Path(__file__).resolve().parent / "blomo" / "__init__.py"
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read_text(), re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Failed to find version string")


setup(
    name="blomo",
    author="Bogdan Lozhkin",
    version=get_version(),
    description="Simple HTTP Load Balencer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kiin/blomo",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["blomo=blomo.main:main"]},
    include_package_data=True,
)