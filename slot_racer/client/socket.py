# Author: Max Greenwald, Pulkit Jain
# 11/30/2018
#
# Module to create a simple interface for persistent socket connections

# package imports
import asyncio
import websockets
import concurrent.futures


async def start():
    """Creates a socket and initiates and runs it
    :return: a coroutine, use asyncio.run(client.start()) to make this work
    """
    skt = Socket()
    skt.connection = await websockets.connect(f'ws://{skt.host}:{skt.port}')
    await skt.handler(None)
    return skt


class Socket(object):
    """Our interface to manage a persistent socket connection

    It is defined by the following attributes:
    - host: string representing the host
    - port: integer representing what port number to connect to
    - connection: the actual websocket

    It is defined by the following behaviors:
    - send(message): sends the messages
    - receive(): TODO
    - handler(path): handles the message consumption and production
    - consumer(message): consumes the passed in message
    - consumer_handler(path): handles consumption
    - producer(): produces messages
    - producer_handler(path): handles production
    """
    def __init__(self, host='localhost', port=8765):
        self.host       = host
        self.port       = port
        self.connection = None

    async def send(self, message):
        await self.connection.send(message)

    # async def receive(self):
    #     print("receiving")
    #     async for message in self.connection:
    #         print("Message")
    #         print(message)

    async def handler(self, path):
        print('handler')
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(path))
        producer_task = asyncio.ensure_future(
            self.producer_handler(path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        print("done")
        for task in pending:
            task.cancel()

    async def consumer(self, message):
        print(message)

    async def consumer_handler(self, path):
        while True:
            message = await self.connection.recv()
            await self.consumer(message)

    async def producer(self):
        name = input("Enter message: ")
        return name

    async def producer_handler(self, path):
        while True:
            message = await self.producer()
            print(f'{message}')
            await self.send(message)


# pending work
def wrap_future(asyncio_future):
    def done_callback(af, cf):
        try:
            cf.set_result(af.result())
        except Exception as e:
            cf.set_exception(e)

    concur_future = concurrent.futures.Future()
    asyncio_future.add_done_callback(lambda f: done_callback(f, cf=concur_future))
    return concur_future
