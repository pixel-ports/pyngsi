#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This agent takes data from a PUSH source, build NGSI entities, eventually writes to a given Sink.
# https://fiware-orion.readthedocs.io/en/2.0.0/user/walkthrough_apiv2/index.html#entity-creation

from pyngsi.agent import NgsiAgent
from pyngsi.sources.source import Row, Source
from pyngsi.sources.server import ServerHttpUpload
from pyngsi.sink import SinkStdout
from pyngsi.ngsi import DataModel


def build_entity(row: Row) -> DataModel:
    id, temperature, pressure = row.record.split(';')
    m = DataModel(id=id, type="Room")
    m.add("temperature", float(temperature))
    m.add("pressure", int(pressure))
    return m


def main():

    # You declare an HTTP server that acts as your Source, listening on port 8080
    src = ServerHttpUpload()

    # If you have an Orion server available, just replace SinkStdout() with SinkOrion()
    sink = SinkStdout()

    # The agent processes CSV content received from the client
    agent = NgsiAgent.create_agent(src, sink, process=build_entity)

    # You must push data to the source, here we send POST requests to the server
    # For example, in a bash shell, send binary content
    # curl --noproxy '*' -v  -H "Content-Type: text/plain" -d $'Room1;23.0;720\nRoom2;21.0;711' "127.0.0.1:8080/upload"
    # You can also send a file, the NGSI datasource provider is set as the filename
    # curl -v -F file=@test.csv http://127.0.0.1:8080/upload
    # CTRL-C to stop the server
    agent.run()

    # The agent provides global statistics on its execution
    agent.close()


if __name__ == '__main__':
    main()
