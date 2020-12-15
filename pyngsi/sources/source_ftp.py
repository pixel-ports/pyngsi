#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Tuple, List, Callable
from loguru import logger
from pyngsi.ftpclient import FtpClient

from pyngsi.sources.source import Source


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
                 provider: str = "user",
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
