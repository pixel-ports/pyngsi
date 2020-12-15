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

    def __init__(self, input: str, provider: str = "user", jsonpath: str = None):
        self.json_obj = input
        self.provider = provider
        self.path = jsonpath

    def __iter__(self):
        obj = self.json_obj
        if self.path:
            obj = self.jsonpath(self.path)

        if isinstance(obj, list):
            for j in obj:
                yield Row(self.provider, j)
        else:
            yield Row(self.provider, obj)

    def jsonpath(self, path: List):
        obj = self.json_obj
        for p in path:
            if isinstance(p, int):
                obj = obj[p]
            else:
                obj = obj.get(p)
        return obj

    def reset(self):
        pass
