#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyngsi.source import Row, SourceSampleOrion
from pyngsi.sink import SinkNull
from pyngsi.agent import NgsiAgent, build_entity_unknown, build_entity_sample_orion


def test_build_entity_unknown():
    m = build_entity_unknown(Row(record="dummy"))
    assert "Unknown:" in m['id']
    assert m['type'] == "Unknown"
    assert m['rawData']['type'] == "Text"
    assert m['rawData']['value'] == "dummy"


def test_build_entity_sample_orion():
    m = build_entity_sample_orion(Row(record="Room1;21.7;720"))
    assert m['id'] == "Room1"
    assert m['type'] == "Room"
    assert m['temperature']['value'] == 21.7
    assert m['temperature']['type'] == "Float"
    assert m['pressure']['value'] == 720
    assert m['pressure']['type'] == "Integer"


def test_agent(mocker):
    src = SourceSampleOrion(count=5, delay=0)
    sink = SinkNull()
    mocker.spy(sink, "write")
    agent = NgsiAgent.create_agent(src, sink)
    agent.run()
    agent.close()
    assert sink.write.call_count == 5  # pylint: disable=no-member
    assert agent.stats == agent.Stats(5, 5, 5, 0, 0)


def test_agent_with_processing(mocker):
    src = SourceSampleOrion(count=5, delay=0)
    sink = SinkNull()
    mocker.spy(sink, "write")
    agent = NgsiAgent.create_agent(src, sink, build_entity_sample_orion)
    agent.run()
    agent.close()
    assert sink.write.call_count == 5  # pylint: disable=no-member
    assert agent.stats == agent.Stats(5, 5, 5, 0, 0)

def test_agent_with_side_effect(mocker):

    def side_effect(row, sink, datamodel):
        print(f"{datamodel=}")

    src = SourceSampleOrion(count=5, delay=0)
    sink = SinkNull()
    mocker.spy(sink, "write")
    agent = NgsiAgent.create_agent(src, sink, build_entity_sample_orion, side_effect)
    agent.run()
    agent.close()
    assert sink.write.call_count == 5  # pylint: disable=no-member
    assert agent.stats == agent.Stats(5, 5, 5, 0, 0)