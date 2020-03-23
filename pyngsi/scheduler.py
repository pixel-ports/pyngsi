#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import socket
import signal
import time
import schedule
import _thread

from flask import Flask, request, jsonify
from cheroot.wsgi import Server as WSGIServer
from loguru import logger
from datetime import datetime
from typing import Callable
from dataclasses import dataclass
from enum import Enum, auto

from pyngsi.sink import Sink
from pyngsi.agent import NgsiAgent, NgsiAgentPull
from pyngsi.__init__ import __version__


class UNIT(Enum):
    seconds = "s"
    minutes = "m"
    hours = "h"
    days = "d"


class SchedulerException(Exception):
    pass


@dataclass
class SchedulerStatus:
    version = __version__
    starttime: datetime = None
    lastcalltime: datetime = None
    calls: int = 0
    calls_success: int = 0
    calls_error: int = 0
    stats: NgsiAgent.Stats = None

    def __init__(self):
        self.starttime = datetime.now()
        self.stats = NgsiAgent.Stats()


class Scheduler():
    """
    Poll takes an agent and polls at periodic intervals.

    Poll updates statitics and provides information (status and version) 
    """
    def __init__(self,
                 agent: NgsiAgentPull,
                 host: str = "0.0.0.0",
                 port: int = 8081,
                 wsgi_port: int = 8880,
                 debug: bool = False,
                 interval: int = 1,
                 unit: UNIT = UNIT.minutes):

        self.agent = agent
        self.host = host
        self.port = port
        self.wsgi_port = wsgi_port
        self.debug = debug
        self.interval = interval
        self.unit = unit
        self.status = SchedulerStatus()

        self.app = Flask(__name__)
        self.app.add_url_rule("/version", 'version',
                              self._version, methods=['GET'])
        self.app.add_url_rule("/status", 'status',
                              self._status, methods=['GET'])

    def _flaskthread(self):
        if self.debug:
            self.app.run(host=self.host, port=self.port, debug=self.debug)
        else:
            wsgi_server = WSGIServer(bind_addr=(
                "0.0.0.0", self.wsgi_port), wsgi_app=self.app, numthreads=100)
            try:
                wsgi_server.start()
            except KeyboardInterrupt:
                wsgi_server.stop()

    def _job(self):
        logger.info(f"start new job at {datetime.now()}")
        self.status.lastcalltime = datetime.now()
        self.status.calls += 1

        # run the NGSI Agent
        try:
            self.agent.run()
        except Exception as e:
            logger.error(f"Error while running job : {e}")
            self.status.calls_error += 1
        else:
            self.status.calls_success += 1

        logger.info(self.agent.stats)

        self.status.stats += self.agent.stats
        self.agent.reset()

    def run(self):
        logger.info(
            f"HTTP server listens on http://{self.host}:{self.port}")
        self.status.starttime = datetime.now()
        _thread.start_new_thread(self._flaskthread, ())

        logger.info("run job now")
        self._job()
        logger.info("schedule job")
        if self.unit == UNIT.seconds:
            schedule.every(self.interval).seconds.do(self._job)
            tick = 1
        elif self.unit == UNIT.minutes:
            schedule.every(self.interval).minutes.do(self._job)
            tick = 4
        elif self.unit == UNIT.hours:
            schedule.every(self.interval).hours.do(self._job)
            tick = 32
        elif self.unit == UNIT.days:
            schedule.every(self.interval).days.do(self._job)
            tick = 128

        while True:
            logger.trace("tick")
            schedule.run_pending()
            time.sleep(tick)

    def _version(self):
        logger.trace("ask for version")
        return jsonify(name="pyngsi", version=__version__)

    def _status(self):
        logger.trace("ask for status")
        remote_status = self.agent.sink.status()
        if remote_status:
            return jsonify(poll_status=self.status,
                           orion_status=remote_status)
        else:
            return jsonify(poll_status=self.status)
