#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sinks.

Sinks MUST respect the following protocol :
Each Sink Class MUST implement write().
Some Sinks MAY override close() if needed to free resources.

SinkOrion is the one you will want to use in your project.
Other sinks such as SinkStdout or SinkFile are useful during the development stage and for unit testing.
"""


import gzip
import requests
import os
import copy

from abc import ABC, abstractmethod
from loguru import logger
from requests_toolbelt.utils import dump

from pyngsi.__init__ import __version__ as version


class Sink(ABC):
    """
    Sink is an abstract class

    The library provides many sinks.
    One can code its own Sink just by extending Sink.
    """

    @abstractmethod
    def write(self, msg):
        pass

    def status(self):
        pass

    def close(self):
        pass


class SinkException(Exception):
    pass


class SinkNull(Sink):
    """Do not write anything. For debugging purpose only."""

    def write(self, msg):
        pass


class SinkStdout(Sink):
    """Write to Standard Output"""

    def write(self, msg):
        print(msg)

# TODO : add append option


class SinkFile(Sink):
    """Write to file"""

    def __init__(self, filename, append=False):
        """
        Parameters
        ----------
        filename : str
            The name of the output file
        """
        self.filename = filename
        try:
            self.file = open(
                self.filename, "a" if append else "w", encoding="utf8")
        except Exception as e:
            raise SinkException(f"cannot open file {self.filename} : {e}")

    def write(self, msg: str):
        try:
            self.file.write(f"{msg}{os.linesep}")
        except Exception as e:
            raise SinkException(f"cannot write to file {self.filename} : {e}")

    def close(self):
        try:
            self.file.close()
        except Exception as e:
            raise SinkException(f"cannot close file {self.filename} : {e}")


class SinkFileGzipped(SinkFile):
    """Write to gzipped file"""

    def __init__(self, filename):
        """
        Parameters
        ----------
        filename : str
            The name of the output file
        """
        self.filename = filename
        try:
            self.file = gzip.open(self.filename, "wt", encoding="utf8")
        except Exception as e:
            raise SinkException(f"cannot open file {self.filename} : {e}")


class SinkHttp(Sink):
    """Send to HTTP server

    Attributes
    ----------
    hostname : str
        Server hostname
    port : int
        Server port
    baseurl: str
        Server Base URL
    useragent: str
        HTTP User-Agent header sent in the request
    status_endpoint: str
        endpoint to ask server for its status and its processing statistics        
    proxy: str
        HTTP Proxy string (i.e http://127.0.0.1:8080)
    """

    def __init__(self, hostname="127.0.0.1", port=8080, secure=False, baseurl="/",
                 post_endpoint="/", post_query="", status_endpoint="/status",
                 useragent=f"NgsiAgent v{version}",
                 proxy=None):
        """
        Parameters
        ----------
        hostname : str
            Server hostname
        port : int
            Server port
        baseurl: str
            Server Base URL
        useragent: str
            HTTP User-Agent header sent in the request
        proxy: str
            HTTP Proxy string (i.e http://127.0.0.1:8080)
        """
        logger.debug("init SinkHttp")
        if (baseurl[0] != "/"):
            raise Exception("baseurl must begin with a slash")

        self.hostname = hostname
        self.port = port
        self.protocol = "https" if secure else "http"
        self.baseurl = baseurl = baseurl.rstrip("/")
        self.post_endpoint = post_endpoint = post_endpoint.rstrip("/")
        self.status_endpoint = status_endpoint = status_endpoint.rstrip("/")
        prefix = f"{self.protocol}://{hostname}:{port}{baseurl}"
        self.post_url = f"{prefix}{post_endpoint}?{post_query}" if post_query else f"{prefix}{post_endpoint}"
        self.status_url = f"{prefix}{status_endpoint}"
        self.proxy = proxy
        self.headers = {'Content-Type': 'application/json',
                        'User-Agent': useragent}
        logger.info(f"{self.baseurl=}")
        logger.info(f"{self.post_url=}")
        logger.info(f"{self.status_url=}")
        logger.info(f"{useragent=}")
        logger.info(f"{self.proxy=}")

    def write(self, msg):
        """Sends HTTP POST request with the NGSI data

        Parameters
        ----------
        msg: str
            the NGSI data
        """

        try:
            r = requests.post(
                self.post_url, msg, headers=self.headers,
                proxies={self.proxy} if self.proxy else None)
            logger.trace(dump.dump_all(r).decode('utf-8'))
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SinkException(
                f"cannot write to SinkHttp : {e}\nServer returned : {r.text}\nrecord={msg}")
        except Exception as e:
            raise SinkException(
                f"cannot write to SinkHttp : {e}\nrecord={msg}")

    def status(self) -> dict:
        logger.debug("ask http server status")
        try:
            if 'Content-Type' in self.headers: # workaround unwanted Content-Type
                headers = self.headers.copy()
                del headers['Content-Type']
            else:
                headers = self.headers()
            r = requests.get(self.status_url, headers=headers)
            logger.trace(dump.dump_all(r).decode('utf-8'))
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
            orion_status = {}
            orion_status['state'] = 'Down or Unreachable'
            orion_status['exception'] = e
            orion_status['server_message'] = r.text
            return orion_status
        except Exception as e:
            logger.error(e)
            orion_status = {}
            orion_status['state'] = 'Down or Unreachable'
            return orion_status


class SinkOrion(SinkHttp):
    """Send to Orion Context Broker"""

    def __init__(self, hostname="127.0.0.1", port="1026", secure=False, baseurl="/",
                 post_endpoint="/v2/entities", post_query="options=upsert", status_endpoint="/version",
                 useragent=f"NgsiAgent v{version}", proxy=None,
                 token=None, service=None, servicepath=None):
        logger.debug("init SinkOrion")
        super().__init__(hostname, port, secure, baseurl,
                         post_endpoint, post_query, status_endpoint,
                         useragent, proxy)
        if 'X-Auth-Token' in self.headers:
            logger.info(
                "A token has already been provided to the pyngsi framework.")
        else:
            if token:
                logger.info("A token has been set programmatically.")
            elif token := os.environ.get('ORION_TOKEN', None):
                logger.info("A token has been found in environment variable.")
            else:
                try:
                    with open('/run/secrets/orion_token') as f:
                        token = f.read()  # 2nd try to get the token from a given file (Docker Secret mode)
                        token = token.rstrip(" \r\n")
                except Exception:
                    pass
                else:
                    logger.info("A token has been found in docker secrets.")
            if token:  # a token has been found
                logger.info("Use token for authentication")
                # add the token to the Authorization header
                self.headers['X-Auth-Token'] = token
            else:
                logger.info(
                    "No token found. Request Orion without authentication.")

        if service is not None:
            self.headers['Fiware-Service'] = service
        if servicepath is not None:
            self.headers['Fiware-ServicePath'] = servicepath
