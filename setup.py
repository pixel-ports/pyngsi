#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyngsi",
    version="1.2.3",
    description="NGSI Python framework intended to build a Fiware NGSI Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pixel-ports/pyngsi",
    author="Fabien Battello",
    author_email="fabien.battello@orange.com",
    license="Apache 2.0",
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=False,
    install_requires=["loguru", "requests", "shortuuid",
                      "more_itertools", "geojson", "flask", "cherrypy", "schedule"],
    python_requires=">=3.8"
)