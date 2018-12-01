# Author: Max Greenwald, Pulkit Jain
# 11/30/2018
#
# Module to create a simple interface for persistent socket connections

# package imports
import asyncio
import websockets
import threading

class Socket(object):
    @classmethod
    async def connect(cls, host, port):
        self = Socket()
        self.connection = await websockets.connect(f'ws://{host}:{port}')
        return self

    async def run(self, receive_message, outgoing_message):
        self.consumer_task = asyncio.ensure_future(self._receive_handler(receive_message))
        self.producer_task = asyncio.ensure_future(self._send_handler(outgoing_message))
        done, pending = await asyncio.wait(
            [self.consumer_task, self.producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

    async def _receive_handler(self, receive_message):
        while True:
            message = await self.connection.recv()
            await receive_message(message)

    async def _send_handler(self, outgoing_message):
        while True:
            message = await outgoing_message()
            await self.connection.send(message)
