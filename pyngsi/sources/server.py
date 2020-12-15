#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import socket
import signal
import time


from flask import Flask, request, jsonify
from cheroot.wsgi import Server as WSGIServer
from loguru import logger
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

from pyngsi.sources.source import Source, SourceStream, SourceSingle
from pyngsi.sources.source_json import SourceJson

from pyngsi.__init__ import __version__ as version


class ServerException(Exception):
    pass


class Server():
    """
    A Server acts both as a Source and as an Agent

    In fact, each time the server receives a request, the server endorses the role of an agent.
    The request content is a source, the server spawns an agent to process it.
    The Server computes is own stats (i.e. incoming requests) and compute ngsi-stats related to the data processing.
    Stats are available at the end when calling the close() method, or at any time, when calling the endpoint status if available.
    """

    def __init__(self, provider="user", ignore_header=False, jsonpath=None):
        self.agent = None
        self.provider = provider
        self.ignore_header = ignore_header
        self.jsonpath = jsonpath

    def set_agent(self, agent):
        self.agent = agent

    def status(self):
        pass

    def close(self):
        pass

    def _process_content(self, src: Source):
        logger.info(f"{src=}")
        from pyngsi.agent import NgsiAgentPull
        if not src:
            logger.info("no source")
            return
        if not self.agent:
            logger.info("agent not set")
            return
        try:
            if self.ignore_header:
                src = src.skip_header()
            agent = NgsiAgentPull(src, self.agent.sink,
                                  self.agent.process, self.agent.side_effect)
            logger.info(f"{self.ignore_header=}")
            logger.info(f"{self.jsonpath=}")
            agent.run()
            agent.close()
            if self.agent:
                self.agent.stats += agent.stats
            return agent.stats
        except Exception as e:
            logger.error(f"cannot parse content : {e}")
            raise ServerException("cannot parse content")


class ServerHttpUpload(Server):
    """
    ServerHttpUpload allows receiving data from HTTP clients

    ServerHttpUpload handles raw binary (curl --data) and multipart/form-data (curl --form).
    ServerHttpUpload handles formats text and json.
    """

    def __init__(self,
                 host: str = "0.0.0.0",
                 port: int = 8081,
                 wsgi_port: int = 8880,
                 endpoint: str = "/upload",
                 debug: bool = False,
                 provider: str = None,
                 ignore_header: bool = False,
                 jsonpath: str = None):

        super().__init__(provider, ignore_header, jsonpath)
        self.host = host
        self.port = port
        self.wsgi_port = wsgi_port
        self.endpoint = endpoint
        self.debug = debug

        self.app = Flask(__name__)
        self.app.add_url_rule("/version", 'version',
                              self._version, methods=['GET'])
        self.app.add_url_rule("/status", 'status',
                              self._status, methods=['GET'])
        self.app.add_url_rule(endpoint, 'upload',
                              self._upload, methods=['POST'])

    def run(self):
        logger.info(
            f"HTTP server listens on http://{self.host}:{self.port}{self.endpoint}")
        if self.agent:
            self.agent.server_status.starttime = datetime.now()

        if self.debug:
            self.app.run(host=self.host, port=self.port, debug=self.debug)
        else:
            wsgi_server = WSGIServer(bind_addr=(
                "0.0.0.0", self.wsgi_port), wsgi_app=self.app, numthreads=100)
            try:
                wsgi_server.start()
            except KeyboardInterrupt:
                wsgi_server.stop()

    def _version(self):
        logger.trace("ask for version")
        return jsonify(name="pyngsi", version=version)

    def _status(self):
        logger.trace("ask for status")
        remote_status = self.agent.sink.status()
        if remote_status:
            return jsonify(server_status=self.agent.server_status,
                           ngsi_stats=self.agent.stats,
                           orion_status=remote_status)
        else:
            return jsonify(server_status=self.agent.server_status,
                           ngsi_stats=self.agent.stats)

    def _upload(self):
        
        if self.agent:
            self.agent.server_status.lastcalltime = datetime.now()
            self.agent.server_status.calls += 1

        logger.info("received request")

        try:

            src, filename = self._create_source(request)

        except Exception as e:
            if self.agent:
                self.agent.server_status.calls_error += 1
            return jsonify({'status': 400, 'message': e})

        logger.info(src)
        stats = self._process_content(src)
        if filename:
            try:
                os.remove(filename)
            except Exception as e:
                logger.warning(f"Cannot remove file {filename}: {e}")

        if self.agent:
            self.agent.server_status.calls_success += 1
        #return jsonify({'status': 200, 'message': 'content uploaded successfully'})
        return jsonify(status=200, message="content uploaded successfully", statistics=stats)

    def _create_source(self, request: request):
        src: Source = None
        filename: str = None
        
        if 'file' in request.files:  # multipart/form-data
            file = request.files['file']
            filename = file.filename
            if filename == "":
                raise ServerException("no file")
            provider = self.provider if self.provider else filename
            ext = (''.join(Path(filename).suffixes))[1:]
            logger.debug(f"{ext=}")
            if ext in Source.registered_extensions:  # extension registred by user
                klass, kwargs = Source.registered_extensions[ext]
                filename = secure_filename(filename)
                file.save(filename)
                src = klass(filename, **kwargs)
            elif ext not in ("txt", "csv", "json"):
                raise ServerException(f"unknown extension {ext}")
            elif ext == 'json':  # JSON extension
                filename = None # here we don't save the file
                data = json.load(file)
                src = SourceJson(data, provider=provider,
                                 jsonpath=self.jsonpath)
            else:  # processed as text
                filename = None # here we don't save the file
                data = file.read().decode('utf-8')
                src = SourceStream(data.splitlines(), provider=provider)
        else:  # raw binary
            if request.is_json:
                logger.info("request is json")
                data = request.get_json()
                src = SourceJson(data, provider=self.provider,
                                 jsonpath=self.jsonpath)
            else:
                logger.info("request is plain text")
                data = request.get_data().decode("utf-8", errors="replace")
                src = SourceStream(data.splitlines())

        return src, filename


class ServerUdp(Server):
    """
    ServerUdp allows receiving UDP frames

    A typical use case is to gather NMEA data from an AIS-receiver.
    """

    def __init__(self,
                 host: str = "127.0.0.1",
                 port: int = 10110,
                 bufsize: int = 1024,
                 provider: str = "UDP Server",
                 ignore_header: bool = False):
        """
        Parameters
        ----------
        host : str
            The server hostname
        port : int
            The server port
        bufsize : int
            Buffer size
        """
        super().__init__(provider, ignore_header)
        self.hostname = host
        self.port = port
        self.bufsize = bufsize
        self.interrupted = False

        logger.info(f"init UDP server addr = {host}:{port}")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        logger.info(f"UDP server started")
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGQUIT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def run(self):
        logger.info("ready...")
        self.agent.server_status.starttime = datetime.now()
        while not self.interrupted:
            logger.info("receiving...")
            try:
                data, addr = self.s.recvfrom(self.bufsize)
                logger.info(f"received UDP message from {addr} : {data}")
                if self.agent:
                    self.agent.server_status.lastcalltime = datetime.now()
                    self.agent.server_status.calls += 1
                src: Source = SourceSingle(
                    data.decode('utf-8'), provider=self.provider)
                self._process_content(src)
                if self.agent:
                    self.agent.server_status.calls_success += 1
            except Exception as e:
                if not self.interrupted:
                    logger.error(e)
                    if self.agent:
                        self.agent.server_status.calls_error += 1

    def close(self):
        self.s.close()
        logger.info(f"UDP server closed")

    def handle_signal(self, signum, frame):
        """Properly clean resources when a signal is received"""
        logger.info("Received SIGNAL : ")
        logger.info("Stopping loop...")
        self.interrupted = True
        self.s.close()
        time.sleep(1)
