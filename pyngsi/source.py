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
import random

from dataclasses import dataclass
from collections.abc import Iterable
from loguru import logger
from os.path import basename
from typing import List, Callable, Tuple, Any, Sequence
from more_itertools import take
from itertools import islice
from zipfile import ZipFile
from io import TextIOWrapper
from pathlib import Path
from deprecated import deprecated

from pyngsi.ftpclient import FtpClient


@dataclass(eq=True, frozen=True)
class Row:
    """
    A row is a data record delivered from a Source.

    A row is composed of the record (the data itself) and the provider (the name of the datasource provider).
    For example, the provider can be the full qualified named of a remote file located on a FTP Server.
    The record could be a simple string, a CSV-delimited line, a full JSON document.
    """
    provider: str = "Unknown"
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
    def from_file(cls, filename: str, provider: str = None, **kwargs):
        """automatically create the Source from a filename, figuring out the extension, handles text, json and gzip compression"""
        if "*" in cls.registered_extensions:
            klass, kwargs = cls.registered_extensions["*"]
            return klass(filename, **kwargs)
        ext = (''.join(Path(filename).suffixes))[1:]
        if ext in cls.registered_extensions:
            klass, kwargs = cls.registered_extensions[ext]
            return klass(filename, **kwargs)
        if ext == "json.gz" or ext == "json":
            return SourceJson(filename, **kwargs)
        return SourceFile(filename, **kwargs)

    @classmethod
    @deprecated(version='1.2.5', reason="This method will be removed soon")
    def create_source_from_file(cls, filename: str, provider: str = None, **kwargs):
        return Source.from_file(filename, provider, **kwargs)

    @classmethod
    def register_extension(cls, ext: str, src, **kwargs):
        cls.registered_extensions[ext] = (src, kwargs)

    @classmethod
    def unregister_extension(cls, ext: str):
        del cls.registered_extensions[ext]

    def reset(self):
        pass


class SourceIter(Source):

    """
    A SourceList is Source built from a Python list.

    """

    def __init__(self, rows: List[str], provider: str = "user"):
        self.rows = rows
        self.provider = provider

    def __iter__(self):
        for record in self.rows:
            yield Row(self.provider, record)

    def reset(self):
        pass


class SourceSingle(Source):

    """
    A SourceSingle is Source built from a Python string.

    """

    def __init__(self, row: str, provider: str = "user"):
        self.row = row
        self.provider = provider

    def __iter__(self):
        yield Row(self.provider, self.row)


class SourceSampleOrion(Source):

    """
    A SourceSampleOrion implements the Source from the NGSI Walkthrough tutorial.

    Please have a look at :
    https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creationhttps://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creation

    First two records are those of the tutorial.
    Following records are randomized.
    """

    def __init__(self, count: int = 5, delay: float = 1.0):
        self.count = count if count > 0 else sys.maxsize
        self.delay = delay

    def __iter__(self):
        i: int = 0
        if self.count >= 1:  # 1st element is fixed
            yield Row("orionSample", "Room1;23;720")
            i += 1
            time.sleep(self.delay)
        if self.count >= 2:  # 2nd element is fixed
            yield Row("orionSample", "Room2;21;711")
            i += 1
            time.sleep(self.delay)
        # next elements are randomized
        while i < self.count:
            yield Row("orionSample", f"Room{i%9+1};{round(random.uniform(-10,50), 1)};{random.randint(700,1000)}")
            i += 1
            time.sleep(self.delay)

    def reset(self):
        pass


class SourceStdin(Source):
    """Read raw data from Standard Input"""

    def __init__(self, provider="stdin"):
        self.stream = sys.stdin
        self.provider = provider

    def __iter__(self):
        for line in self.stream:
            yield Row(self.provider, line.rstrip("\r\n"))

    def reset(self):
        pass


class SourceFile(Source):
    """Read raw data from a text file. File may be gzipped. File may be a single-file ZIP archive."""

    def __init__(self, filename: str, provider: str = None, ignore_header: bool = False):
        """
        Parameters
        ----------
        filename : str
            The name of the file containing raw data
        """
        self.filename = filename
        self.provider = provider if provider else basename(filename)
        self.ignore_header = ignore_header

        try:
            if self.filename[-3:] == ".gz":
                self.stream = gzip.open(self.filename, "rt", encoding="utf-8")
            elif self.filename[-4:] == ".zip":
                zf = ZipFile(self.filename, 'r')
                f = zf.namelist()[0]
                self.stream = TextIOWrapper(zf.open(f, 'r'), encoding='utf-8')
            else:
                self.stream = open(self.filename, "r", encoding="utf-8")
        except Exception as e:
            logger.critical(f"Cannot open file {self.filename} : {e}")
            sys.exit(1)

    def __iter__(self):
        if self.ignore_header:
            next(self.stream)
        for line in self.stream:
            yield Row(self.provider, line.rstrip("\r\n"))

    def reset(self):
        self.__init__(self.filename, self.provider)


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


# a file downloaded from FTP : (local_filename, remote_filename)
FtpFile = Tuple[str, str]


class SourceFtp(Source):
    """
    A SourceFtp reads data from a given FTP Server.

    All the complexity is hidden for the end user.
    The SourceFtp can automatically download the desired files from the FTP Server.
    Selection of the remote files is based on the filenames, and operates inside one or many remote folders.
    The selection is operated thanks to the f_match() function that could be a regex or whatever you want.
    Once the files are downloaded (into a temp dir), the connection to the FTP Server is closed.
    Then the Source reads the downloaded files to deliver rows as usual, by iterating on file records.
    At the end, when the Source is closed, the temp dir is cleaned.
    """

    def __init__(self, host: str, user: str = "anonymous",
                 passwd: str = "guest",
                 paths: List[str] = ["/pub"],
                 use_tls: bool = False,
                 f_match: Callable[[str], bool] = lambda x: False,
                 provider: str = None,
                 source_factory=Source.from_file):
        """
        Parameters
        ----------
        filename : str
            The name of the file containing raw data
        """

        self.host = host
        self.user = user
        self.passwd = passwd
        self.use_tls = use_tls
        self.paths = paths
        self.f_match = f_match
        self.provider = provider
        self.source_factory = source_factory

        # connect to FTP server
        self.ftp = FtpClient(host, user, passwd, use_tls)

        # retrieve a list of files we're interested in
        remote_files = self._retrieve_filelist(paths, f_match)

        # download files : a list of (local_filename, remote_filename)
        self.downloaded_files: List[FtpFile] = self._download_files(
            remote_files)

        if len(self.downloaded_files) != len(remote_files):
            logger.critical(f"Some files have not been downloaded.")

        # disconnect from FTP server
        self.ftp.close()

    def __iter__(self):
        for ftpfile in self.downloaded_files:
            localname, remotename = ftpfile
            logger.info(f"process local {localname}")
            provider = self.provider if self.provider else f"ftp://{self.host}{remotename}"
            source = self.source_factory(localname, provider)
            yield from source
        self.ftp.clean()

    def _retrieve_filelist(self, paths, f_match=lambda x: True) -> List[str]:
        remote_files = []
        for path in paths:
            filelist = [x for x in self.ftp.retrieve_filelist(
                path) if f_match(x)]
            remote_files.extend(filelist)
        logger.info(f"Found {len(remote_files)} matching files")
        return remote_files

    def _download_files(self, remote_files: List[str]) -> List[FtpFile]:
        try:
            downloaded_files = [(self.ftp.download(remote), remote)
                                for remote in remote_files]
        except Exception as e:
            logger.critical(f"Problem while downloading files : {e}")
        return downloaded_files

    def reset(self):
        self.__init__(self.host, self.user, self.passwd,
                      self.paths, self.f_match, self.provider, self.source_factory)
