#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from dataclasses import dataclass
from shortuuid import uuid
from loguru import logger
from datetime import datetime
from typing import Callable, Union
from abc import ABC, abstractmethod

from pyngsi.sources.source import Row, Source, SourceStream
from pyngsi.sink import Sink, SinkStdout
from pyngsi.ngsi import DataModel
from pyngsi.sources.server import Server
from pyngsi.__init__ import __version__


class NgsiException(Exception):
    pass


class NgsiAgent(ABC):

    """
    Abstract Class used by either NgsiAgentPull or NgsiAgentServer.
    """

    @property
    @abstractmethod
    def status(self):
        pass

    @staticmethod
    def create_agent(src: Union[Source, Server] = SourceStream(sys.stdin),
                     sink: Sink = SinkStdout(),
                     process: Callable = lambda x: x.record,
                     side_effect: Callable[[Row, Sink, DataModel], int] = None):
        """
        Factory method to create the agent depending on the source push/pull.

        :param src: the Source
        :param sink: the Sink
        :param process: a function that takes an input row from the source and outputs a NGSI datamodel
        """
        if isinstance(src, Source):
            return NgsiAgentPull(src, sink, process, side_effect)
        elif isinstance(src, Server):
            return NgsiAgentServer(src, sink, process, side_effect)
        else:
            raise NgsiException(
                f"Cannot create agent. Unknown source type {type(src)}")

    @abstractmethod
    def run(self):
        """
        Run the NGSI Agent
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close the NGSI Agent
        """
        pass

    @dataclass(eq=True)
    class Stats:
        """
        Agent processing statistics
        """
        input: int = 0
        processed: int = 0
        output: int = 0
        filtered: int = 0
        error: int = 0
        side_entities: int = 0

        def __add__(self, o):
            return NgsiAgent.Stats(self.input + o.input,
                                   self.processed + o.processed,
                                   self.output + o.output,
                                   self.filtered + o.filtered,
                                   self.error + o.error,
                                   self.side_entities + o.side_entities)

        def __iadd__(self, o):
            self.input += o.input
            self.processed += o.processed
            self.output += o.output
            self.filtered += o.filtered
            self.error += o.error
            self.side_entities += o.side_entities
            return self

        def zero(self):
            self.input = 0
            self.processed = 0
            self.output = 0
            self.filtered = 0
            self.error = 0
            self.side_entities = 0
            return self

class NgsiAgentPull(NgsiAgent):

    """
    The NgsiAgentPull pulls rows from the datasource
    """

    def __init__(self,
                 source: Source = None,
                 sink: Sink = None,
                 process: Callable = lambda row, *args, **kwargs: row.record,
                 side_effect: Callable = None):
        logger.info("init NGSI agent")
        self.source = source if source else SourceStream(sys.stdin)
        logger.info(f"source = [{self.source.__class__.__name__}]")
        self.sink = sink if sink else SinkStdout()
        logger.info(f"sink = [{self.sink.__class__.__name__}]")
        self.process = process
        self.side_effect = side_effect
        self.stats = NgsiAgent.Stats()

    @property
    def status(self):
        return self.stats

    def run(self):
        logger.info("start to acquire data")
        for row in self.source:
            logger.debug(row)
            try:
                if row.provider is None:
                    row.provider = "user"
                logger.trace(f"{row.provider=}\t{row.record=}")
                self.stats.input += 1
                x = self.process(row)
                if not x:
                    self.stats.filtered += 1
                    continue
                self.stats.processed += 1
                msg = x.json() if isinstance(x, DataModel) else x
                self.sink.write(msg)
                self.stats.output += 1
                if self.side_effect:
                    side_entities = self.side_effect(row, self.sink, x)
                    self.stats.side_entities += side_entities
            except Exception as e:
                self.stats.error += 1
                logger.error(f"Cannot process record : {e}")
        return self

    def close(self):
        logger.info("close NGSI agent")
        logger.info(self.status)
        # logger.info(f"close source")
        # self.source.close()
        logger.info(f"close sink")
        self.sink.close()

    def reset(self):
        self.source.reset()
        self.stats.zero()


class NgsiAgentServer(NgsiAgent):

    """
    The NgsiAgentServer processes data from a push datasource.

    The NgsiAgentServer acts both as a Source and as an Agent.
    In this case, the Source is a Server that listens from incoming data.
    Each time the Source receives a data request, the NgsiAgentServer is triggered to process the request content.
    """

    import pyngsi.sources.server

    @dataclass
    class ServerStatus:
        version = __version__
        starttime: datetime = None
        lastcalltime: datetime = None
        calls: int = 0
        calls_success: int = 0
        calls_error: int = 0

        def __init__(self):
            self.starttime = datetime.now()

    def __init__(self,
                 server: pyngsi.sources.server.Server = None,
                 sink: Sink = None,
                 process: Callable = lambda row, *args, **kwargs: row.record,
                 side_effect: Callable[[Row, Sink, DataModel], int] = None):
        logger.info("init NGSI agent")
        self.server = server
        logger.info(f"server = [{self.server.__class__.__name__}]")
        self.sink = sink if sink else SinkStdout()
        logger.info(f"sink = [{self.sink.__class__.__name__}]")
        self.process = process
        logger.info(f"process = [{self.process}]")
        self.side_effect = side_effect
        logger.info(f"side_effect = [{self.side_effect}]")
        self.server_status = self.ServerStatus()
        self.stats = NgsiAgent.Stats()

    @property
    def status(self):
        return self.server_status, self.stats

    def run(self):
        logger.info("start server")
        self.start_time = datetime.now()

        server: Server = self.server
        server.set_agent(self)  # a NGSI server also acts as an agent
        logger.info(f"{server.agent=}")

        self.server.run()
        return self

    def close(self):
        logger.info("close NGSI agent")
        logger.info(self.status)
        logger.info(f"close server")
        self.server.close()
        logger.info(f"close sink")
        self.sink.close()


def build_entity_unknown(row: Row) -> DataModel:
    """
    Helper function to quickly build a datamodel without the need of id and type.
    """
    m = DataModel(id=f"Unknown:{uuid()}", type="Unknown")
    m.add("rawData", row.record)
    return m


def build_entity_sample_orion(row: Row) -> DataModel:
    """
    Helper function to build a datamodel for the NGSI walkthrough tutorial.

    Please have a look at : https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creation
    Here we consider the input as a CSV line.
    """
    id, temperature, pressure = row.record.split(';')
    m = DataModel(id=id, type="Room")
    m.add("temperature", float(temperature))
    m.add("pressure", int(pressure))
    return m
