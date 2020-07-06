#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pkg_resources

from typing import List

from pyngsi.source import Row, Source, SourceStream, SourceSingle, SourceStdin, \
    SourceSampleOrion, SourceFile, SourceJson


def test_method_limit():
    src = SourceSampleOrion(count=5, delay=0)
    src = src.limit(2)
    assert isinstance(src, Source)
    lines = [x for x in src]
    assert len(lines) == 2


def test_method_head():
    src = SourceSampleOrion(count=5, delay=0)
    r = src.head(3)
    assert isinstance(r, list)
    assert len(r) == 3


def test_method_first():
    src = SourceSampleOrion(count=5, delay=0)
    row: Row = src.first()
    assert row.provider == "orionSample"


def test_method_skip_header():
    src = SourceSampleOrion(count=5, delay=0)
    src = src.skip_header(lines=2)
    lines = [x for x in src]
    assert len(lines) == 3


def test_source_list():
    src = SourceStream(["test1", "test2"])
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0] == Row('user', 'test1')
    assert rows[1] == Row('user', 'test2')


def test_source_single():
    src = SourceSingle("test1")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 1
    assert rows[0] == Row('user', 'test1')


def test_source_stdin(mocker):
    mocker.patch('sys.stdin', {"input1", "input2"})
    src = SourceStdin()
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    # pytest capture input/output could mess the order
    assert Row('stdin', 'input1') in rows
    assert Row('stdin', 'input2') in rows


def test_source_sample_orion():
    src = SourceSampleOrion(count=5, delay=0)
    rows: List[Row] = [x for x in src]
    assert len(rows) == 5
    assert rows[0] == Row('orionSample', 'Room1;23;720')
    assert rows[1] == Row('orionSample', 'Room2;21;711')
    assert "Room5;" in rows[4].record


def test_source_file(mocker):
    input_data = 'input1\ninput2\n'
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("builtins.open", mock_open)
    src = SourceFile("test.txt")
    rows: List[Row] = [x for x in src]
    assert rows == [Row('test.txt', 'input1'), Row('test.txt', 'input2')]


def test_source_file_gz(mocker):
    input_data = 'input3\ninput4\n'
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("gzip.open", mock_open)
    src = SourceFile("test.txt.gz")
    rows: List[Row] = [x for x in src]
    assert rows == [Row('test.txt.gz', 'input3'), Row('test.txt.gz', 'input4')]


def test_source_file_zip():
    zipname = pkg_resources.resource_filename(__name__, "data/test.txt.zip")
    src = SourceFile(zipname)
    rows: List[Row] = [x for x in src]
    assert rows == [Row('test.txt.zip', 'input5'),
                    Row('test.txt.zip', 'input6')]


def test_source_json(mocker):
    input_data = r"""{
    "fruit": "Apple",
    "size": "Large",
    "color": "Red"
}"""
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("builtins.open", mock_open)
    src = SourceJson("test.json")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 1
    assert rows[0].provider == "test.json"
    assert rows[0].record["fruit"] == "Apple"


def test_source_json_array(mocker):
    input_data = r"""[ {"fruit": "Apple", "size": "Large", "color": "Red"},
    {"fruit": "Lime", "size": "Medium", "color": "Yellow"} ]"""
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("builtins.open", mock_open)
    src = SourceJson("test.json")
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
    src = SourceJson("test.json", path=["dataset", "data"])
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].provider == "test.json"
    assert rows[0].record["fruit"] == "Apple"
    assert rows[1].provider == "test.json"
    assert rows[1].record["fruit"] == "Lime"