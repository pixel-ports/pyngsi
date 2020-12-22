# pyngsi

[![PyPI Latest Release](https://img.shields.io/pypi/v/pyngsi)](https://pypi.org/project/pyngsi/)
[![License badge](https://img.shields.io/github/license/pixel-ports/pyngsi)](https://opensource.org/licenses/Apache-2.0)
[![Build badge](https://img.shields.io/travis/pixel-ports/pyngsi)](https://travis-ci.org/pixel-ports/pyngsi/)
[![Code coverage](https://img.shields.io/codecov/c/github/pixel-ports/pyngsi/master)](https://codecov.io/gh/pixel-ports/pyngsi)
[![Python version](https://img.shields.io/pypi/pyversions/pyngsi)](https://pypi.org/project/pyngsi/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/pixel-ports/pyngsi-tutorial/master)
[![Powered by Fiware](https://img.shields.io/badge/powered%20by-Fiware-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)](https://www.fiware.org/)
<!--[![Package Status](https://img.shields.io/pypi/status/pixel-ports)](https://pypi.org/project/pyngsi/)-->

## What is it ?

``pyngsi`` is a Python framework that helps you write a pipeline for your [Fiware](https://www.fiware.org) dataflow.<br>

Writing a [NGSI](https://fiware.github.io/specifications/ngsiv2/stable) agent that relies on pyngsi avoids all the plumbing so you can focus on writing your own logic to build [NGSI](https://fiware.github.io/specifications/ngsiv2/stable) entities.

## Key Features

- [NGSI v2](https://fiware.github.io/specifications/ngsiv2/stable/) support
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

## Getting started

### Build your first NGSI entity

```python
from pyngsi.ngsi import DataModel

m = DataModel(id="Room1", type="Room")
m.add_url("dataProvider", "https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creation")
m.add("pressure", 720)
m.add("temperature", 23.0)

m.pprint()
```

The resulting JSON looks like this :

```json
{
  "id": "Room1",
  "type": "Room",
  "dataProvider": {
    "value": "https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creation",
    "type": "URL"
  },
  "pressure": {
    "value": 720,
    "type": "Integer"
  },
  "temperature": {
    "value": 23.0,
    "type": "Float"
  }
}
```

### Send the NGSI entity to the Orion broker

```python
from pyngsi.sink import SinkOrion

sink = SinkOrion()
sink.write(m.json())
```

### Develop your own NGSI Agent

Let's quickly create a CSV file to store values from our room sensors
```bash
echo -e "Room1;23;720\nRoom2;21;711" > room.csv
```

Let's code a function that converts incoming rows to NGSI entities

```python
def build_entity(row: Row) -> DataModel:
    id, temperature, pressure = row.record.split(';')
    m = DataModel(id=id, type="Room")
    m.add_url("dataProvider", row.provider)
    m.add("temperature", float(temperature))
    m.add("pressure", int(pressure))
    return m
```

Let's use it in in our new NGSI Agent

```python
from pyngsi.sources.source import Source, Row
from pyngsi.sink import SinkOrion
from pyngsi.agent import NgsiAgent

src = Source.from_file("room.csv")
sink = SinkOrion()
agent = NgsiAgent.create_agent(src, sink, process=build_entity)
agent.run()
```

This basic example shows how the pyngsi framework is used to build a NGSI Agent.<br>
Here data are stored on the local filesystem.<br>
By changing just one line you could retrieve incoming data from a FTP server or HTTP server.

```python
from pyngsi.sources.source import Source, Row
from pyngsi.sources.server import ServerHttpUpload
from pyngsi.sink import SinkOrion
from pyngsi.agent import NgsiAgent

src = ServerHttpUpload() # line updated !
sink = SinkOrion()
agent = NgsiAgent.create_agent(src, sink, process=build_entity)
agent.run()
```

The HTTP server is running. Now you can send the file to the endpoint.
```bash
curl -F file=@room.csv http://127.0.0.1:8880/upload
```

JSON and text formats are natively supported.<br>
Many sources and sinks are provided, i.e. *SinkStdout* to just displays entities, eliminating the need of having an Orion server running.<br>
One could create a custom Source to handle custom data. The *MicrosoftExcelSource* is given as exemple.<br>
One could extend the framework according to his needs.

## Dependencies
- [loguru](https://github.com/Delgan/loguru)
- [requests](https://2.python-requests.org)
- [requests-toolbelt](https://github.com/requests/toolbelt)
- [shortuuid](https://github.com/skorokithakis/shortuuid)
- [more_itertools](https://github.com/more-itertools/more-itertools)
- [geojson](https://github.com/jazzband/geojson)
- [flask](https://palletsprojects.com/p/flask)
- [cherrypy](https://cherrypy.org)
- [schedule](https://github.com/dbader/schedule)
- [openpyxl](https://openpyxl.readthedocs.io)

## License

[Apache 2.0](LICENSE)

## Documentation
The official documentation is hosted at https://pixel-ports.github.io/pyngsi-tutorial.html

## Known Issues
SourceMicrosoftExcel may fail to open some odd Excel files due to an openpyxl bug (i.e. sometimes cannot read graphs).<br>
In this case try to remove the offending sheet or prefer working with CSV files.
## Background
Work on ``pyngsi`` started at [Orange](https://www.orange.com) in 2019 for the needs of the [PIXEL](https://pixel-ports.eu) european project.

## Funding

``pyngsi`` has been developed as part of the [PIXEL](https://pixel-ports.eu) project, H2020, funded by the EC under Grant Agreement number [769355](https://cordis.europa.eu/project/id/769355).