#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This agent takes data from the standard input, performs a basic computation, eventually writes to the standard output.
# Note : a Sink expects a NGSI DataModel class as input. If it is not the case it simply writes the string representation of its input
# Use CTRL-D to send EOF

from pyngsi.agent import NgsiAgent
from pyngsi.sources.source import Row


def basic_processing(data: Row):
    # A data row is the output of the Source.
    # It is a simple dataclass composed of :
    # - the name of the datasource provider : here stdin
    # - the data record itself : here a line typed in by the user
    # The function can takes additional arguments if needed by the processing logic
    _ = data.provider  # for this example, we don't consider the datasource provider
    return data.record.replace("ping", "pong")


def main():
    agent = NgsiAgent.create_agent(process=basic_processing)
    # We could have used a lambda, or any function which a Row as a first argument, even an object method
    # agent = NgsiAgent(process=lambda x: x.record.replace("ping", "pong"))
    # agent = NgsiAgent(process=myObject.basic_processing)
    agent.run()
    agent.close()


if __name__ == '__main__':
    main()
