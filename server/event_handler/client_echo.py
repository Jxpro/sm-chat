#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""调试client与server通信"""

from common.message import MessageType


def run(sc, parameters):
    # pprint(['client echo', parameters])
    sc.send(MessageType.server_echo, parameters)
