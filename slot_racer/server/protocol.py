# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module defining the protocol for the server

# package imports
import time


async def ping(ws):
    """Returns the max of four roundrtip times between client and server"""
    repeat, times = 4, []
    for _ in range(repeat):
        start = time.process_time()
        await ws.send('ping')
        await ws.recv()
        end = time.process_time()
        times.append(end - start)
    return max(times)


def get_protocol():
    protocol = dict()
    protocol['ping'] = ping
    return protocol


