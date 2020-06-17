#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pkg_resources

from pyngsi.more_sources import SourceMicrosoftExcel


def test_source():
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    src = SourceMicrosoftExcel(filename)
    rows = [row for row in src]
    assert len(rows) == 4
    assert rows[0].provider == "test.xlsx"
    assert rows[0].record == "SH1HDR1,,,"
    assert rows[1].record == "SH1HDR2,,,"
    assert rows[2].record == "data1,11,12,13"
    assert rows[3].record == "data2,14,15,16"


def test_source_with_ignore_header():
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    src = SourceMicrosoftExcel(filename, ignore=1)
    rows = [row for row in src]
    assert len(rows) == 3
    assert rows[0].provider == "test.xlsx"
    assert rows[0].record == "SH1HDR2,,,"
    assert rows[1].record == "data1,11,12,13"
    assert rows[2].record == "data2,14,15,16"


def test_source_with_sheetname():
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    src = SourceMicrosoftExcel(filename, sheetname="Sheet2")
    rows = [row for row in src]
    assert len(rows) == 4
    assert rows[0].provider == "test.xlsx"
    assert rows[0].record == "SH2HDR1,,,"
    assert rows[1].record == "SH2HDR2,,,"
    assert rows[2].record == "data1,21,22,23"
    assert rows[3].record == "data2,24,25,26"


def test_source_with_sheetid():
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    src = SourceMicrosoftExcel(filename, sheetid=1)
    rows = [row for row in src]
    assert len(rows) == 4
    assert rows[0].provider == "test.xlsx"
    assert rows[0].record == "SH2HDR1,,,"
    assert rows[1].record == "SH2HDR2,,,"
    assert rows[2].record == "data1,21,22,23"
    assert rows[3].record == "data2,24,25,26"
