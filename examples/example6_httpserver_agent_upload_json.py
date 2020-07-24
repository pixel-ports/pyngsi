#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This agent takes data from a PUSH source, build NGSI entities, eventually writes to a given Sink.
# https://fiware-orion.readthedocs.io/en/2.0.0/user/walkthrough_apiv2/index.html#entity-creation

from pyngsi.agent import NgsiAgent
from pyngsi.sources.source import Row
from pyngsi.sources.server import ServerHttpUpload
from pyngsi.sink import SinkStdout
from pyngsi.ngsi import DataModel


def build_entity(row: Row) -> DataModel:
    r = row.record
    m = DataModel(id=r["room"], type="Room")
    m.add("temperature", r["temperature"])
    m.add("pressure", r["pressure"])
    return m


def main():

    # You declare an HTTP server that acts as your Source, listening on port 8080
    src = ServerHttpUpload()

    # If you have an Orion server available, just replace SinkStdout() with SinkOrion()
    sink = SinkStdout()

    # The agent processes JSON content received from the client
    agent = NgsiAgent.create_agent(src, sink, process=build_entity)

    # You must push data to the source, here we send POST requests to the server
    # For example, in a bash shell, type in :
    # curl -X POST -H "Content-Type: application/json" -d '{"room":"Room1","temperature":23.0,"pressure":710}' http://127.0.0.1:8080/upload
    # You could also send a JSON Array. For example, type in :
    # curl -X POST -H "Content-Type: application/json" -d '[{"room":"Room1","temperature":23.0,"pressure":710},{"room":"Room2","temperature":21.0,"pressure":711}]' http://127.0.0.1:8080/upload
    # You can also send a file, the NGSI datasource provider is set as the filename
    # curl -v -F file=@test.json http://127.0.0.1:8080/upload
    # CTRL-C to stop the server
    agent.run()

    # The agent provides global statistics on its execution
    agent.close()


if __name__ == '__main__':
    main()
