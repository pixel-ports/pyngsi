#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import gzip

from typing import Tuple, List, Callable
from loguru import logger
from os.path import basename
from zipfile import ZipFile
from io import TextIOWrapper

from pyngsi.sources.source import Row, Source


class SourceJson(Source):
    """Read JSON formatted data from Standard Input"""

    def jsonpath(self, path: List):
        obj = self.json_obj
        for p in path:
            if isinstance(p, int):
                obj = obj[p]
            else:
                obj = obj.get(p)
        return obj

    def __init__(self, input: str = None, provider: str = None, path: str = None):
        self.provider = provider
        self.path = path
        if not isinstance(input, str):
            self.json_obj = input
        else:
            filename = input
            self.provider = basename(filename) if filename else "stdin"
            if filename:
                if filename[-3:] == ".gz":
                    stream = gzip.open(filename, "rt", encoding="utf-8")
                elif filename[-4:] == ".zip":
                    zf = ZipFile(filename, 'r')
                    f = zf.namelist()[0]
                    self._cm = TextIOWrapper(zf.open(f, 'r'), encoding='utf-8')
                else:
                    stream = open(filename, "r", encoding="utf-8")
            else:
                stream = sys.stdin
            self.json_obj = json.load(stream)

    def __iter__(self):
        obj = self.json_obj
        if self.path:
            obj = self.jsonpath(self.path)

        if isinstance(obj, list):
            for j in obj:
                yield Row(self.provider, j)
        else:
            yield Row(self.provider, obj)

    def reset(self):
        pass
