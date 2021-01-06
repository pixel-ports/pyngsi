#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyngsi",
    version="2.1.7",
    description="NGSI Python framework intended to build a Fiware NGSI Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pixel-ports/pyngsi",
    author="Fabien Battello",
    author_email="fabien.battello@orange.com",
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9"
    ],
    packages=setuptools.find_packages(),
    include_package_data=False,
    install_requires=["loguru", "requests", "requests-toolbelt", "shortuuid",
                      "more_itertools", "geojson", "flask", "cherrypy", "schedule", "openpyxl"],
    test_requires=["pytest", "pytest-mock", "requests-mock", "pytest-flask"],
    python_requires=">=3.8"
)
