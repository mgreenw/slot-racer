# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module defining the protocol for the server

# package imports
import time
from statistics import mean
from datetime import datetime
import json

ping_message = json.dumps(dict(
    type='ping',
    data=None
))

async def ping(ws):
    """Returns the max of four roundrtip times between client and server"""
    repeat, times = 50, []
    for _ in range(repeat):
        start = datetime.now()
        await ws.send(ping_message)
        await ws.recv()
        end = datetime.now()
        times.append((end - start).total_seconds())
    return mean(times)


def get_protocol():
    protocol = dict()
    protocol['pong'] = ping
    return protocol


