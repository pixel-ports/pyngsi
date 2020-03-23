#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from loguru import logger
from os.path import basename

from pyngsi.ftpclient import FtpClient


@pytest.fixture
def mock_ftp(mocker):
    mocker.patch("ftplib.FTP.connect")
    mocker.patch("ftplib.FTP.sock")
    mocker.patch("ftplib.FTP.login",
                 side_effect=lambda u, _: logger.info(f"mock FTP login({u}, ******)"))
    mocker.patch("ftplib.FTP.quit",
                 side_effect=lambda: logger.info("mock FTP quit()"))
    mocker.patch("ftplib.FTP.close",
                 side_effect=lambda: logger.info("mock FTP close()"))
    mocker.patch('ftplib.FTP.retrlines', side_effect=mocked_ftp_retrlines)
    mocker.patch('ftplib.FTP.retrbinary', side_effect=mocked_ftp_retrbinary)


def mocked_ftp_retrlines(cmd, callback):
    logger.info("mock FTP retrlines()")
    for year in range(2018, 2020):
        callback(f"/pub/data/noaa/{year}/166220-99999-{year}.gz")


def mocked_ftp_retrbinary(cmd, callback):
    logger.info("mock FTP retrbinary()")
    callback(b"1;23.0;720")


def test_retrieve_filelist(mock_ftp):
    ftp = FtpClient("ftp.ncdc.noaa.gov")
    filelist = ftp.retrieve_filelist("/pub/data/noaa/2019")
    ftp.close()
    assert len(filelist) == 2
    assert filelist[0] == "/pub/data/noaa/2018/166220-99999-2018.gz"
    assert filelist[1] == "/pub/data/noaa/2019/166220-99999-2019.gz"
    ftp.clean()


def test_download(mock_ftp):
    ftp = FtpClient("ftp.ncdc.noaa.gov")
    localfile = ftp.download("/pub/data/noaa/2018/166220-99999-2018")
    ftp.close()
    assert basename(localfile) == "166220-99999-2018"
    with open(localfile) as f:
        read_data = f.read()
    assert read_data == "1;23.0;720"
    ftp.clean()
