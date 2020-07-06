#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import gzip

from zipfile import ZipFile
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, Tuple


def stream_from(filename: str) -> Tuple[Iterable, str]:
    try:
        ext = Path(filename).suffix
        if ext == ".gz":
            stream = gzip.open(filename, "rt", encoding="utf-8")
            filename = Path(filename).stem
            return stream, filename
        elif ext == ".zip":
            zf = ZipFile(filename, 'r')
            f = zf.namelist()[0]
            stream = TextIOWrapper(zf.open(f, 'r'), encoding='utf-8')
            filename = Path(filename).stem
            return stream, filename
        else:
            return open(filename, "r", encoding="utf-8"), filename
    except Exception as e:
        print(f"Cannot open file {filename} : {e}", file=sys.stderr)
