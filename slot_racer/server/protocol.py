# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module defining the protocol for the server

# package imports
import time
from statistics import mean
from datetime import datetime
import json
from ..communication import Serializer

serializer = Serializer()

ping_message = serializer.compose('ping', None)

async def ping(ws):
    """Returns the average time of a ping between the client and the server"""
    repeat, times = 50, []
    for _ in range(repeat):
        start = datetime.now()
        await ws.send(ping_message)
        await ws.recv()
        end = datetime.now()
        times.append((end - start).total_seconds())
    return mean(times) / 2


def get_protocol():
    protocol = dict()
    protocol['pong'] = ping
    return protocol


