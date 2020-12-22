#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip

from zipfile import ZipFile
from io import TextIOWrapper
from pathlib import Path
from loguru import logger


def stream_from(filename: str = None):
    try:
        suffixes = Path(filename).suffixes
        ext = suffixes[-1]
        if ext == ".gz":
            stream = gzip.open(filename, "rt", encoding="utf-8")
            return stream, suffixes[:-1]
        elif ext == ".zip":
            zf = ZipFile(filename, 'r')
            f = zf.namelist()[0]
            stream = TextIOWrapper(zf.open(f, 'r'), encoding='utf-8')
            return stream, suffixes[:-1]
        else:
            return open(filename, "r", encoding="utf-8"), suffixes
    except Exception as e:
        logger.error(f"Cannot open file {filename} : {e}")
