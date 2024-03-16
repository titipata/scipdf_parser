#! /usr/bin/env python
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt" ,"r") as f:
    requirements = list(map(lambda x: x.strip(), f.readlines()))

if __name__ == "__main__":

    setup(
        name='scipdf',
        version='0.1dev',
        description=' Python parser for scientific PDF based on GROBID.',
        long_description=long_description,
        long_description_content_type="text/markdown",
        url='https://github.com/titipata/scipdf_parser',
        author='Titipat Achakulvisut',
        author_email='my.titipat@gmail.com',
        license='(c) MIT License 2019 Titipat Achakulvisut',
        install_requires=requirements ,
        packages=find_packages(),
        keywords=[
            "PDF parser",
            "GROBID",
            "Python PDF parser"
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
