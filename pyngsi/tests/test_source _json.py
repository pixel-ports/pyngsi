#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pkg_resources

from typing import List

from pyngsi.sources.source import Row, Source
from pyngsi.sources.source_json import SourceJson


def test_source_json(mocker):
    input_data = r"""{
    "fruit": "Apple",
    "size": "Large",
    "color": "Red"
    }"""

    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("builtins.open", mock_open)
    src = Source.from_file("test.json")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 1
    assert rows[0].provider == "test.json"
    assert rows[0].record["fruit"] == "Apple"


def test_source_json_array(mocker):
    input_data = r"""[ {"fruit": "Apple", "size": "Large", "color": "Red"},
    {"fruit": "Lime", "size": "Medium", "color": "Yellow"} ]"""
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("builtins.open", mock_open)
    src = Source.from_file("test.json")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].provider == "test.json"
    assert rows[0].record["fruit"] == "Apple"
    assert rows[1].provider == "test.json"
    assert rows[1].record["fruit"] == "Lime"


def test_source_json_path(mocker):
    input_data = r"""{"dataset": {"data": [ {"fruit": "Apple", "size": "Large", "color": "Red"},
    {"fruit": "Lime", "size": "Medium", "color": "Yellow"} ] } }"""
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("builtins.open", mock_open)
    src = Source.from_file("test.json", jsonpath=["dataset", "data"])
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].provider == "test.json"
    assert rows[0].record["fruit"] == "Apple"
    assert rows[1].provider == "test.json"
    assert rows[1].record["fruit"] == "Lime"
