#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyngsi.sources.source import Source
from pyngsi.sources.more_sources import SourceMicrosoftExcel

Source.register_extension('xlsx', SourceMicrosoftExcel, ignore=1)
src = Source.from_file("test.xlsx") # replace with your file

# print rows (first sheet used if many)
for row in src:
    print(row.record)
    