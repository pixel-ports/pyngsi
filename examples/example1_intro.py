#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Just the default agent that takes data from the standard input and writes as-is to the standard output
# Note : a Sink expects a NGSI DataModel class as input. If it is not the case it simply writes the string representation of the its input
# Use CTRL-D to send EOF
from pyngsi.agent import NgsiAgent


def main():
    agent = NgsiAgent.create_agent()
    agent.run()
    agent.close()


if __name__ == '__main__':
    main()
