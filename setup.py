#! /usr/bin/env python
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    setup(
        name='scipdf',
        version='1.0.3',
        description=' Python parser for scientific PDF based on GROBID.',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/skuam/scipdf_parser',
        author='Titipat Achakulvisut, Mateusz Jakubnczak',
        author_email='my.titipat@gmail.com, mateusz.jakubczak.contact+githubSciPDfParser@gmail.com',
        license='(c) MIT License 2023 Titipat Achakulvisut, Mateusz Jakubczak',
        install_requires=['lxml', 'requests', 'spacy', 'pandas', 'textstat', "pydantic", "beautifulsoup4"],
        packages=find_packages(),
        keywords=[
            "PDF parser",
            "GROBID",
            "Python PDF parser",
            "Pydantic",
            "Scientific PDF parser",
            "Scientific PDF",
            "PDF",
        ],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        package_data={
            'scipdf': ['pdf/pdffigures2/*.jar']
        },
        scripts=['serve_grobid.sh'],
    )
