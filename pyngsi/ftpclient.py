#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ftplib
import tempfile
import shutil

from loguru import logger
from ftplib import FTP
from typing import List
from os.path import basename, join


class FtpClientException(Exception):
    pass


class FtpClient():

    def __init__(self, host: str, user: str = "anonymous",
                 passwd: str = "guest"):
        logger.debug("Connect to FTP server")
        self.ftp = FTP(host)
        try:
            self.ftp.login(user, passwd)
        except ftplib.error_perm as e:
            error_code = int(str(e).split()[0])
            if (error_code == 503):
                logger.info("Already connected. Continue.")
            else:
                raise FtpClientException(f"Cannot connect : {e}")
        except ftplib.all_errors as e:
            raise FtpClientException(f"Cannot connect : {e}")
        try:
            # create temp dir to receive future downloads
            self.tmpdir = tempfile.mkdtemp()
        except Exception as e:
            logger.critical(f"Cannot create temp dir : {e}")

    def retrieve_filelist(self, path: str) -> List[str]:
        filelist: List[str] = []
        self.ftp.retrlines(f"NLST {path}", filelist.append)
        return filelist

    def download(self, remote: str) -> str:
        logger.debug(f"Download file {remote}")
        try:
            local = join(self.tmpdir, basename(remote))
            handle = open(local, 'wb')
            self.ftp.retrbinary(f"RETR {remote}", handle.write)
            handle.close()
        except Exception as e:
            raise FtpClientException(f"Cannot download {remote} : {e}")
        return local

    def close(self):
        logger.debug("Disconnect from FTP server")
        try:
            self.ftp.quit()
            self.ftp.close()
        except Exception as e:
            raise FtpClientException(f"Cannot disconnect : {e}")

    def clean(self):
        if self.tmpdir:
            try:
                shutil.rmtree(self.tmpdir)
            except Exception as e:
                logger.error(f"Cannot remove temp directory : {e}")
