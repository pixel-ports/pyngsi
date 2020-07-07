#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import re

from loguru import logger
from os.path import basename, join

from pyngsi.sources.source_ftp import SourceFtp


@pytest.fixture
def mock_ftp(mocker):
    mocker.patch("ftplib.FTP.connect")
    mocker.patch("ftplib.FTP.sock")
    mocker.patch("ftplib.FTP.login", side_effect=lambda u,
                 _: logger.info(f"mock FTP login({u}, ******)"))
    mocker.patch("ftplib.FTP.quit",
                 side_effect=lambda: logger.info("mock FTP quit"))
    mocker.patch("ftplib.FTP.close",
                 side_effect=lambda: logger.info("mock FTP close"))


@pytest.fixture
def mock_tempfile(mocker):
    mocker.patch('tempfile.mkdtemp')


@pytest.fixture
def mock_ftpclient(mocker):
    mocker.patch("pyngsi.ftpclient.FtpClient.retrieve_filelist",
                 side_effect=mocked_retrieve_filelist)
    mocker.patch("pyngsi.ftpclient.FtpClient.download",
                 side_effect=mocked_download)


def mocked_retrieve_filelist(paths):
    logger.info("mock FtpClient retrieve_filelist()")
    filelist = []
    for year in range(2018, 2020):
        for usaf in ("166220", "166240", "166270"):
            filelist.append(f"/pub/data/noaa/{year}/{usaf}-99999-{year}.gz")
    return filelist


def mocked_download(remote):
    logger.info("mock FtpClient download()")
    return join("/tmp", basename(remote))


def test_retrieve_all_files(mock_ftp, mock_tempfile, mock_ftpclient):
    src = SourceFtp("ftp.ncdc.noaa.gov", paths=["/pub/data/noaa/2019"], f_match=lambda x: True)
    assert len(src.downloaded_files) == 6
    assert ("/tmp/166240-99999-2019.gz", "/pub/data/noaa/2019/166240-99999-2019.gz") in src.downloaded_files
    assert ("/tmp/166270-99999-2019.gz", "/pub/data/noaa/2019/166270-99999-2019.gz") in src.downloaded_files


def test_retrieve_some_files(mock_ftp, mock_tempfile, mock_ftpclient):
    pattern = fr".*/{166220}-\d{{5}}-\d{{4}}.gz$"
    prog = re.compile(pattern)
    src = SourceFtp("ftp.ncdc.noaa.gov", paths=["/pub/data/noaa"], f_match=lambda x: prog.match(x))
    assert len(src.downloaded_files) == 2
    assert ("/tmp/166220-99999-2018.gz", "/pub/data/noaa/2018/166220-99999-2018.gz") in src.downloaded_files
    assert ("/tmp/166220-99999-2019.gz", "/pub/data/noaa/2019/166220-99999-2019.gz") in src.downloaded_files
