#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import json

from pyngsi.server import ServerHttpUpload
from pyngsi.__init__ import __version__ as version


@pytest.fixture
def app():
    src = ServerHttpUpload()
    return src.app


def test_version(client):
    response = client.get("/version")
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert version == data['version']


def test_upload(client):
    data = {
        'room': 'Room1',
        'temperature': 23.0,
        'pressure': 710}
    response = client.post("/upload", json=data)
    assert response.status_code == 200
