#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyngsi.agent import NgsiAgentPull


def main():
    agent = NgsiAgentPull()
    agent.run()
    agent.close()


if __name__ == '__main__':
    main()
