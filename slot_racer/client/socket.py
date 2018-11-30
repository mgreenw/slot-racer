import asyncio
import websockets
from threading import Thread
import concurrent.futures

# spawn a thread that works as the listener

async def consumer(message):
    print(message)

async def consumer_handler(websocket, path):
    while True:
        message = await websocket.recv()
        await consumer(message)

async def producer():
    await asyncio.sleep(1)
    return "ping"

async def producer_handler(websocket, path):
    while True:
        message = await producer()
        print("sending" + message)
        await websocket.send(message)

async def handler(websocket, path):
    print('handler')
    consumer_task = asyncio.ensure_future(
        consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(
        producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    print("done")
    for task in pending:
        task.cancel()

class Socket(object):
    @classmethod
    async def connect(cls, host='localhost', port=8765):
        self = Socket()
        self.connection = await websockets.connect(f'ws://{host}:{port}')
        await handler(self.connection, None)
        return self

    async def send(self, message):
        await self.connection.send(message)

    # async def receive(self):
    #     print("receiving")
    #     async for message in self.connection:
    #         print("Message")
    #         print(message)

if __name__ == '__main__':
    socket = asyncio.run(Socket.connect())

# I want to run
async def connect():
    connection = await websockets.connect('ws://localhost:8765')
    return connection

def wrap_future(asyncio_future):
    def done_callback(af, cf):
        try:
            cf.set_result(af.result())
        except Exception as e:
            cf.set_exception(e)

    concur_future = concurrent.futures.Future()
    asyncio_future.add_done_callback(lambda f: done_callback(f, cf=concur_future))
    return concur_future
