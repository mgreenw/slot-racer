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

async def empty_receive(message):
    pass

async def empty_outgoing():
    while True:
        await asyncio.sleep(10)

def _run_socket(receive_message, outgoing_message, host, port):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    socket = asyncio.get_event_loop().run_until_complete(Socket.connect(host, port))
    asyncio.get_event_loop().run_until_complete(socket.run(receive_message, outgoing_message))

def run_socket(receive_message=empty_receive, outgoing_message=empty_outgoing, host='localhost', port=8765):
    socket = threading.Thread(target=_run_socket, args=[receive_message, outgoing_message, host, port])
    socket.start()
    return socket
