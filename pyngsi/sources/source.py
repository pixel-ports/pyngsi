#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Source for NGSI Agents to collect from.

Sources MUST respect the following protocol :
Each Source Class is a generator hence MUST implement __iter__().
Some Sources MAY implement close() if needed to free resources.
"""

import sys
import gzip
import json
import time
import glob

from dataclasses import dataclass
from collections.abc import Iterable
from loguru import logger
from os.path import basename
from typing import List, Callable, Tuple, Any, Sequence
from more_itertools import take
from itertools import islice, chain
from zipfile import ZipFile
from io import TextIOWrapper
from pathlib import Path

from pyngsi.utils import stream_from


@dataclass(eq=True)
class Row:
    """
    A row is a data record delivered from a Source.

    A row is composed of the record (the data itself) and the provider (the name of the datasource provider).
    For example, the provider can be the full qualified named of a remote file located on a FTP Server.
    The record could be a simple string, a CSV-delimited line, a full JSON document.
    """
    provider: str = "user"
    record: Any = None


class Source(Iterable):
    """
    A Source is a pull datasource : any datasource we can iterate on.

    The library provides many sources.
    One can code its own Source just by extending Source, and providing a new Row for each iteration.
    """

    registered_extensions = {}

    def __init__(self, rows: Sequence[Row]):
        self.rows = rows

    def __iter__(self):
        yield from self.rows

    def head(self, n: int = 10) -> List[Row]:
        """return a list built from the first n elements"""
        return take(n, self)

    def first(self) -> Row:
        """return the first element"""
        row: Row = None
        try:
            row = self.head(1)[0]
        except Exception:
            pass
        return row

    def skip_header(self, lines: int = 1):
        """return a new Source with first n lines skipped, default is to skip only the first line"""
        return Source(islice(self, lines, None))

    def limit(self, n: int = 10):
        """return a new Source limited to the first n elements"""
        iterator = iter(self)
        return Source((next(iterator) for _ in range(n)))

    @classmethod
    def from_stream(cls, stream: Iterable = sys.stdin, provider: str = "user", **kwargs):
        """automatically create the Source from a stream"""
        return SourceStream(stream, **kwargs)

    @classmethod
    def from_file(cls, filename: str, provider: str = "user", **kwargs):
        from pyngsi.sources.source_json import SourceJson
        """automatically create the Source from a filename, figuring out the extension, handles text, json and gzip compression"""
        if "*" in cls.registered_extensions:
            klass, kwargs = cls.registered_extensions["*"]
            return klass(filename, **kwargs)
        ext = (''.join(Path(filename).suffixes))[1:]
        if ext in cls.registered_extensions:
            klass, kwargs = cls.registered_extensions[ext]
            return klass(filename, **kwargs)
        stream, suffixes = stream_from(filename)
        ext = suffixes[-1]
        if ext == ".json":
            json_obj = json.load(stream)
            return SourceJson(json_obj, provider=basename(filename), **kwargs)
        return SourceStream(stream, provider=basename(filename), **kwargs)

    @classmethod
    def from_files(cls, filenames: Sequence[str], provider: str = "user", **kwargs):
        sources = [Source.from_file(f) for f in filenames]
        return SourceMany(sources)

    @classmethod
    def from_glob(cls, pattern: str, provider: str = "user", **kwargs):
        sources = [Source.from_file(f) for f in glob.glob(pattern)]
        return SourceMany(sources)   

    @classmethod
    def from_globs(cls, patterns: Sequence[str], provider: str = "user", **kwargs):
        filenames = chain.from_iterable([glob.glob(p) for p in patterns])
        sources = [Source.from_file(f) for f in filenames]
        return SourceMany(sources)        

    @classmethod
    def register_extension(cls, ext: str, src, **kwargs):
        cls.registered_extensions[ext] = (src, kwargs)

    @classmethod
    def unregister_extension(cls, ext: str):
        if cls.is_registered_extension(ext):
            del cls.registered_extensions[ext]

    @classmethod
    def is_registered_extension(cls, ext: str):
        return ext in cls.registered_extensions

    @classmethod
    def register(cls, src, **kwargs):
        cls.register_extension("*", src, **kwargs)

    @classmethod
    def unregister(cls):
        cls.unregister_extension("*")

    def reset(self):
        pass


class SourceStream(Source):

    def __init__(self, stream: Iterable, provider: str = "user", ignore_header: bool = False):
        if ignore_header:
            next(stream)
        self.stream = stream
        self.provider = provider

    def __iter__(self):
        for line in self.stream:
            yield Row(self.provider, line.rstrip("\r\n"))

    def reset(self):
        pass


class SourceStdin(SourceStream):

    def __init__(self, **kwargs):
        super().__init__(stream=sys.stdin, **kwargs)


class SourceSingle(Source):

    """
    A SourceSingle is Source built from a Python string.

    """

    def __init__(self, row: Any, provider: str = "user"):
        self.row = row
        self.provider = provider

    def __iter__(self):
        yield Row(self.provider, self.row)


class SourceMany(Source):

    def __init__(self, sources: Sequence[Source], provider: str = "user"):
        self.sources = sources
        self.provider = provider

    def __iter__(self):
        for src in self.sources:
            yield from src
