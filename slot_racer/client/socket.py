# Author: Max Greenwald, Pulkit Jain
# 11/30/2018
#
# Module to create a simple interface for persistent socket connections

# package imports
import asyncio
import websockets
import threading
from .extra import Queue


async def start(skt):
    await skt.run()


class Socket(object):
    """Our interface to manage a persistent socket connection

        It is defined by the following attributes:
        - host: string representing the host
        - port: integer representing what port number to connect to
        - connection: the actual websocket
        - swap_time: time to swap execution between receiver and sender
        - inbox: Incoming messages Queue
        - outbox: Outgoing messages Queue
        - running: Boolean representing whether Socket is running or not

        It is defined by the following behaviors:
        - raise_error_uninit(): Raises error if the socket is not initialized
        - run(): Handles the message consumption and production
        - _receive_handler(): handles message consumption
        - _outgoing_message(): handle message production
    """
    def __init__(self, host='localhost', port=8765):
        self.host       = host
        self.port       = port
        self.connection = None
        self.swap_time  = 0.01
        self.inbox      = Queue()
        self.outbox     = Queue()
        self.running    = True

    def raise_error_uninit(self):
        if not self.connection:
            raise Exception("Socket not started. \n"
                            "USAGE: asyncio.run(socket.start(...) to use this.")

    async def run(self):
        self.connection = await websockets.connect(f'ws://{self.host}:'
                                                   f'{self.port}')
        outbox_thread = threading.Thread(target=self._send_handler)
        outbox_thread.start()
        consumer_task = asyncio.ensure_future(self._receive_handler())
        done, pending = await asyncio.wait(
            [consumer_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        outbox_thread.join()

    async def _receive_handler(self):
        self.raise_error_uninit()
        async for message in self.connection:
            self.inbox.put(message)
            await asyncio.sleep(self.swap_time)

    def _send_handler(self):
        self.raise_error_uninit()
        while self.running:
            message = self.outbox.get()
            asyncio.run(self.connection.send(message))


