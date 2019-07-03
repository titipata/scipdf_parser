#! /usr/bin/env python
from setuptools import setup

if __name__ == "__main__":
    setup(
        name='scipdf',
        version='0.1dev',
        description=' Python parser for scientific PDF based on GROBID.',
        url='https://github.com/titipata/scipdf_parser',
        author='Titipat Achakulvisut',
        author_email='my.titipat@gmail.com',
        license='(c) MIT License 2019 Titipat Achakulvisut',
        install_requires=['lxml', 'requests', 'spacy', 'pandas', 'textstat'],
        packages=['scipdf'],
        package_data={
            'pubmed_parser.data': ['*.pdf'],
        }
    )
