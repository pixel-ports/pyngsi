# pyngsi

[![PyPI Latest Release](https://img.shields.io/pypi/v/pyngsi)](https://pypi.org/project/pyngsi/)
[![License badge](https://img.shields.io/github/license/pixel-ports/pyngsi)](https://opensource.org/licenses/Apache-2.0)
[![Build badge](https://img.shields.io/travis/pixel-ports/pyngsi)](https://travis-ci.org/pixel-ports/pyngsi/)
[![Code coverage](https://img.shields.io/codecov/c/github/pixel-ports/pyngsi/master)](https://codecov.io/gh/pixel-ports/pyngsi)
[![Python version](https://img.shields.io/pypi/pyversions/pyngsi)](https://pypi.org/project/pyngsi/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pixel-ports/pyngsi-tutorial/master)
[![NGSI v2](https://nexus.lab.fiware.org/repository/raw/public/badges/specifications/ngsiv2.svg)](https://fiware.github.io/specifications/ngsiv2/stable/)
[![Powered by Fiware](https://img.shields.io/badge/powered%20by-Fiware-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://www.fiware.org/)
<!--[![Package Status](https://img.shields.io/pypi/status/pixel-ports)](https://pypi.org/project/pyngsi/)-->

## What is it ?

``pyngsi`` is a Python framework that helps you write a pipeline for your [Fiware](https://www.fiware.org) dataflow.<br>

Writing a [NGSI](https://fiware.github.io/specifications/ngsiv2/stable) agent that relies on pyngsi avoids all the plumbing so you can focus on writing your own logic to build [NGSI](https://fiware.github.io/specifications/ngsiv2/stable) entities.

## Key Features

- Map Python-native data to NGSI entities
- Write NGSI entities to Fiware [Orion](https://fiware-orion.readthedocs.io/en/master)
- Handle incoming data through a common interface
- Compute statistics
- Allow visualization/debugging facilities

## Where to get it
The source code is currently hosted on GitHub at :
https://github.com/pixel-ports/pyngsi

Binary installer for the latest released version is available at the [Python
package index](https://pypi.org/project/pyngsi).

```sh
pip install pyngsi
```

## Dependencies
- [loguru](https://github.com/Delgan/loguru)
- [requests](https://2.python-requests.org)
- [shortuuid](https://github.com/skorokithakis/shortuuid)
- [more_itertools](https://github.com/more-itertools/more-itertools)
- [geojson](https://github.com/jazzband/geojson)
- [flask](https://palletsprojects.com/p/flask)
- [cherrypy](https://cherrypy.org)
- [schedule](https://github.com/dbader/schedule)
- [openpyxl](https://openpyxl.readthedocs.io)
- [Deprecated](https://github.com/tantale/deprecated)

## License

[Apache 2.0](LICENSE)

## Documentation
The official documentation is hosted at https://pixel-ports.github.io/pyngsi-tutorial.html

## Background
Work on ``pyngsi`` started at [Orange](https://www.orange.com) in 2019 for the needs of the [PIXEL](https://pixel-ports.eu) european project.

## Funding

``pyngsi`` has been developed as part of the [PIXEL](https://pixel-ports.eu) project, H2020, funded by the EC under Grant Agreement number [769355](https://cordis.europa.eu/project/id/769355).