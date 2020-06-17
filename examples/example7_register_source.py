#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyngsi.source import Source
from pyngsi.more_sources import SourceMicrosoftExcel

Source.register_extension('xlsx', SourceMicrosoftExcel, ignore=1)
src = Source.create_source_from_file("test.xlsx") # replace with your file

# print rows (first sheet used if many)
for row in src:
    print(row.record)
    