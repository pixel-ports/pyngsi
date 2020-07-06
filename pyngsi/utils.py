#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import gzip

from zipfile import ZipFile
from io import TextIOWrapper
from typing import Iterable


def stream_from(filename: str) -> Iterable:
    try:
        if filename[-3:] == ".gz":
            return gzip.open(filename, "rt", encoding="utf-8")
        elif filename[-4:] == ".zip":
            zf = ZipFile(filename, 'r')
            f = zf.namelist()[0]
            return TextIOWrapper(zf.open(f, 'r'), encoding='utf-8')
        else:
            return open(filename, "r", encoding="utf-8")
    except Exception as e:
        print(f"Cannot open file {filename} : {e}", file=sys.stderr)
