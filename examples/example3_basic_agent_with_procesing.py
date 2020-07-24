#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This agent takes data from a sample source, builds NGSI entities, eventually writes to a given Sink.
# https://fiware-orion.readthedocs.io/en/2.0.0/user/walkthrough_apiv2/index.html#entity-creation

from pyngsi.agent import NgsiAgent
from pyngsi.sources.source import Row
from pyngsi.sources.more_sources import SourceSampleOrion
from pyngsi.sink import SinkStdout
from pyngsi.ngsi import DataModel


def build_entity(row: Row) -> DataModel:
    id, temperature, pressure = row.record.split(';')
    m = DataModel(id=id, type="Room")
    m.add("temperature", float(temperature))
    m.add("pressure", int(pressure))
    return m


def main():
    src = SourceSampleOrion()
    # if you have an Orion server available, just replace SinkStdout() with SinkOrion()
    sink = SinkStdout()
    agent = NgsiAgent.create_agent(src, sink, process=build_entity)
    agent.run()
    agent.close()


if __name__ == '__main__':
    main()
