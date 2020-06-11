#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ftplib
import ssl
import tempfile
import shutil

from loguru import logger
from ftplib import FTP, FTP_TLS
from typing import List
from os.path import basename, join

# https://stackoverflow.com/questions/14659154/ftpes-session-reuse-required
class MyFTP_TLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,
                                            server_hostname=self.host,
                                            session=self.sock.session)  # this is the fix
        return conn, size


class FtpClientException(Exception):
    pass


class FtpClient():

    def __init__(self, host: str, user: str = "anonymous",
                 passwd: str = "guest", use_tls: bool = False):
        logger.debug("Connect to FTP server")
        if use_tls:
            self.ftp = MyFTP_TLS(host)
            self.ftp.ssl_version = ssl.PROTOCOL_TLS
        else:
            self.ftp = FTP(host)
        try:
            self.ftp.login(user, passwd)
            self.ftp.set_pasv(True)
            if use_tls:
                self.ftp.prot_p()
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
