"""
File containing the required information to successfully build a python package
"""

import setuptools

with open("README.md", "r", encoding="utf-8", newline="\n") as fh:
    long_description = fh.read()

setuptools.setup(
    name='hl_hello_world',
    version='1.1.1',
    packages=setuptools.find_packages(),
    install_requires=[],
    author="Henry Letellier",
    author_email="henrysoftwarehouse@protonmail.com",
    description="A module that provides the good old 'Hello World !' string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hanra-s-work/workflow_verisoning",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
