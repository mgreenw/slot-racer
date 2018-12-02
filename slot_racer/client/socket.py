# Author: Max Greenwald, Pulkit Jain
# 11/30/2018
#
# Module to create a simple interface for persistent socket connections

# package imports
import asyncio
import websockets
import threading


async def start(client, host, port, receive_message, outgoing_message):
    """Creates a socket and initiates and runs it
    :param: client: the client that will be using this socket
    :param: host: host of server
    :param: port: port of server
    :param: receive_message: a function to handle messages received
    :param: outgoing_message: a function to handle messages sent
    """
    skt = Socket(host, port)
    skt.connection = await websockets.connect(f'ws://{skt.host}:{skt.port}')
    client.socket = skt
    await skt.run(receive_message, outgoing_message)
    # TODO: close the socket/deinit the socket??


class Socket(object):
    """Our interface to manage a persistent socket connection

        It is defined by the following attributes:
        - host: string representing the host
        - port: integer representing what port number to connect to
        - connection: the actual websocket
        - swap_time: time to swap execution between receiver and sender

        It is defined by the following behaviors:
        - run(receive_message, outgoing_message): handles the message
              consumption and production
        - _receive_handler(receive_message): handles message consumption
        - _outgoing_message(outgoing_message): handle message production
    """
    def __init__(self, host='localhost', port=8765):
        self.host       = host
        self.port       = port
        self.connection = None
        self.swap_time  = 0.01

    def raise_error_uninit(self):
        if not self.connection:
            raise Exception("Socket not started. \n"
                            "USAGE: asyncio.run(socket.start(...) to use this.")

    async def run(self, recv, outg):
        self.raise_error_uninit()
        consumer_task = asyncio.ensure_future(self._receive_handler(recv))
        producer_task = asyncio.ensure_future(self._send_handler(outg))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()

    async def _receive_handler(self, receive_message):
        self.raise_error_uninit()
        async for message in self.connection:
            receive_message(message)
            await asyncio.sleep(self.swap_time)

    async def _send_handler(self, outgoing_message):
        self.raise_error_uninit()
        while True:
            message = outgoing_message()
            if message:
                await self.connection.send(message)
            await asyncio.sleep(self.swap_time)


