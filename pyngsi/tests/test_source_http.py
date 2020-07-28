#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import requests
import _thread
import time
import pkg_resources

from io import BytesIO

from pyngsi.sources.server import ServerHttpUpload
from pyngsi.sources.source import Source
from pyngsi.sources.more_sources import SourceMicrosoftExcel
from pyngsi.sink import SinkNull
from pyngsi.agent import NgsiAgent


@pytest.fixture(scope="module")
def init_agent():
    global agent
    Source.register_extension("xlsx", SourceMicrosoftExcel)
    src = ServerHttpUpload()
    sink = SinkNull()
    agent = NgsiAgent.create_agent(src, sink)
    _thread.start_new_thread(agent.run, ())
    time.sleep(1)  # let time for the server to setup
    yield
    assert agent.server_status.calls == 3
    agent.close()
    time.sleep(1)  # let time for the server to shutdown


def test_agent_upload_multipart(init_agent):
    multipart_form_data = {'file': ("room.csv", BytesIO(b'Room1;23;710'))}
    response = requests.post(
        'http://127.0.0.1:8880/upload', files=multipart_form_data)
    assert response.status_code == 200
    assert agent.stats == NgsiAgent.Stats(1, 1, 1, 0, 0, 0)
    agent.stats.zero()


def test_agent_upload_multipart_excel(init_agent):
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    multipart_form_data = {'file': ("test.xlsx", open(filename, 'rb'))}
    response = requests.post(
        'http://127.0.0.1:8880/upload', files=multipart_form_data)
    assert response.status_code == 200
    assert agent.stats == NgsiAgent.Stats(4, 4, 4, 0, 0, 0)
    agent.stats.zero()


def test_upload_raw_json(init_agent):
    data = {
        'room': 'Room1',
        'temperature': 23.0,
        'pressure': 710}
    response = requests.post('http://127.0.0.1:8880/upload', json=data)
    assert response.status_code == 200
    assert agent.stats == NgsiAgent.Stats(1, 1, 1, 0, 0, 0)
    agent.stats.zero()
