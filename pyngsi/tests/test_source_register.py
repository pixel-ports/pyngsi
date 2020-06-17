#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pkg_resources

from pyngsi.source import Source
from pyngsi.more_sources import SourceMicrosoftExcel


def test_register_source():
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    Source.register_extension("xlsx", SourceMicrosoftExcel)
    src = Source.create_source_from_file(filename)
    rows = [row for row in src]
    assert len(rows) == 4
    assert rows[0].provider == "test.xlsx"
    assert rows[0].record == "SH1HDR1,,,"
    assert rows[1].record == "SH1HDR2,,,"
    assert rows[2].record == "data1,11,12,13"
    assert rows[3].record == "data2,14,15,16"

def test_register_source_with_args():
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    Source.register_extension("xlsx", SourceMicrosoftExcel, sheetid=1, ignore=1)
    src = Source.create_source_from_file(filename)
    rows = [row for row in src]
    assert len(rows) == 3
    assert rows[0].provider == "test.xlsx"
    assert rows[0].record == "SH2HDR2,,,"
    assert rows[1].record == "data1,21,22,23"
    assert rows[2].record == "data2,24,25,26"
